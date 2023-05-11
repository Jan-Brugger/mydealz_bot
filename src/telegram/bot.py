from __future__ import annotations

import asyncio
import html
import json
import logging
import os
import traceback
from os import getenv
from pickle import UnpicklingError
from time import sleep
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import PickleStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message, ParseMode, Update
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound, TelegramAPIError, Unauthorized

from src.config import Config
from src.db.constants import UColumns
from src.db.tables import SQLiteNotifications, SQLiteUser
from src.exceptions import NotificationNotFoundError, TooManyNotificationsError, UserNotFoundError
from src.models import DealModel, NotificationModel, UserModel
from src.telegram import keyboards, messages
from src.telegram.callbacks import ALLOWED_CHARACTERS, ALLOWED_SEPARATORS, Actions, AddNotificationCB, BroadcastCB, \
    Commands, HomeCB, NotificationCB, SettingsActions, SettingsCB, States
from src.telegram.filters import BlacklistedFilter, NotWhitelistedFilter
from src.telegram.helpers import finish_state, get_callback_var, get_chat_id, get_notification, overwrite_or_answer, \
    store_notification_id

QUERY_PATTERN = rf'^[{ALLOWED_SEPARATORS}{ALLOWED_CHARACTERS}]+$'
QUERY_PATTERN_LIMITED_CHARS = rf'^[{ALLOWED_SEPARATORS}{ALLOWED_CHARACTERS}]{{1,58}}$'
PRICE_PATTERN = r'^\d+([,\.]\d{1,2})?$'


# pylint: disable=too-many-locals,too-many-statements
class TelegramBot:
    def __init__(self) -> None:
        self.bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)

        try:
            storage = PickleStorage(path=Config.CHAT_FILE)
        except UnpicklingError:
            os.remove(Config.CHAT_FILE)
            sleep(3)
            storage = PickleStorage(path=Config.CHAT_FILE)

        dispatcher = Dispatcher(bot=self.bot, storage=storage)

        @dispatcher.message_handler(NotWhitelistedFilter(), state='*')
        async def not_whitelisted(message: Message) -> None:
            await SQLiteUser().set_user_state(get_chat_id(message), False)

            await message.answer(
                messages.user_not_whitelisted()
            )

        @dispatcher.message_handler(BlacklistedFilter(), state='*')
        async def blacklisted(message: Message) -> None:
            await message.answer(
                messages.user_blacklisted()
            )

        @dispatcher.message_handler(commands=Commands.START, state='*')
        @dispatcher.callback_query_handler(HomeCB.filter(), state='*')
        async def start(
                telegram_object: Message | CallbackQuery,
                state: FSMContext | None = None,
                callback_data: dict[str, Any] | None = None
        ) -> None:
            await finish_state(state)

            try:
                user = await SQLiteUser().get_by_id(get_chat_id(telegram_object))
            except UserNotFoundError:
                logging.info(
                    'User started the bot first time.\nUser: %s\nLocale:%s', telegram_object.from_user,
                    telegram_object.from_user.locale
                )
                user = UserModel().parse_telegram_object(telegram_object)
                logging.info('added user: %s', user.__dict__)

                await SQLiteUser().upsert_model(user)

            if not user.active:
                await SQLiteUser().set_user_state(user.id, True)

            notifications = await SQLiteNotifications().get_by_user_id(user.id)

            await overwrite_or_answer(
                telegram_object=telegram_object,
                text=messages.start(user),
                reply_markup=keyboards.start(notifications, get_callback_var(callback_data, 'page', int)),
                reply_instead_of_edit=get_callback_var(callback_data, 'reply', bool)
            )

        @dispatcher.message_handler(commands=Commands.PING, state='*')
        async def ping_handler(message: Message) -> None:
            await message.answer('pong')

        @dispatcher.message_handler(commands=Commands.HELP, state='*')
        async def help_handler(telegram_object: Message | CallbackQuery) -> None:
            await overwrite_or_answer(
                telegram_object,
                messages.help_msg(),
                reply_markup=keyboards.home_button()
            )

        @dispatcher.message_handler(commands=Commands.SETTINGS, state='*')
        async def settings(
                telegram_object: Message | CallbackQuery,
                state: FSMContext | None = None
        ) -> None:
            await finish_state(state)

            user = await SQLiteUser().get_by_id(get_chat_id(telegram_object))
            await overwrite_or_answer(
                telegram_object,
                messages.settings(user),
                reply_markup=keyboards.settings(user)
            )

        @dispatcher.message_handler(commands=Commands.BROADCAST, state='*')
        async def broadcast(
                telegram_object: Message | CallbackQuery,
                state: FSMContext | None = None
        ) -> None:
            await finish_state(state)

            if get_chat_id(telegram_object) != int(getenv('OWN_ID') or 0):
                return

            await States.BROADCAST.set()
            await overwrite_or_answer(telegram_object, messages.broadcast_start())

        @dispatcher.message_handler(state=States.BROADCAST)
        async def broadcast_validate(message: Message, state: FSMContext) -> None:
            await finish_state(state)
            await message.reply(
                text=messages.broadcast_verify(),
                reply_markup=keyboards.broadcast_message(message.message_id)
            )

        @dispatcher.callback_query_handler(BroadcastCB.filter())
        async def broadcast_send(
                query: CallbackQuery,
                state: FSMContext,
                callback_data: dict[str, Any]
        ) -> None:
            await finish_state(state)

            message_id = get_callback_var(callback_data, 'message_id', int)
            if not message_id:
                return

            users = await SQLiteUser().get_all_active_user_ids()
            sent_to = 0
            for user_id in users:
                try:
                    await self.bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=getenv('OWN_ID'),
                        message_id=message_id,
                        disable_notification=True
                    )
                    sent_to += 1
                except (Unauthorized, ChatNotFound):
                    logging.info('User %s blocked the bot. Disable him', user_id)
                    await SQLiteUser().set_user_state(user_id, False)
                except TelegramAPIError as error:
                    logging.error('Failed to send broadcast-message. %s', error)

            await overwrite_or_answer(query, messages.broadcast_sent(sent_to, len(users)))

        @dispatcher.callback_query_handler(AddNotificationCB.filter(query=''))
        async def add_notification(query: CallbackQuery) -> None:
            await States.ADD_NOTIFICATION.set()
            await overwrite_or_answer(query.message, messages.query_instructions())

        @dispatcher.message_handler(regexp=QUERY_PATTERN, state=States.ADD_NOTIFICATION)
        @dispatcher.callback_query_handler(AddNotificationCB.filter())
        async def process_add_notification(
                telegram_object: Message | CallbackQuery,
                state: FSMContext,
                callback_data: dict[str, Any] | None = None
        ) -> None:
            await state.finish()

            notification_query = get_callback_var(callback_data, 'query', str) or telegram_object.text
            chat_id = get_chat_id(telegram_object)
            notification = await SQLiteNotifications().save_notification(notification_query, chat_id)

            await overwrite_or_answer(
                telegram_object,
                messages.notification_added(notification),
                reply_markup=keyboards.notification_commands(notification)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.VIEW))
        async def show_notification(
                query: CallbackQuery,
                callback_data: dict[str, Any]
        ) -> None:
            notification = await get_notification(callback_data)
            await overwrite_or_answer(
                query.message,
                messages.notification_overview(notification),
                reply_markup=keyboards.notification_commands(notification),
                reply_instead_of_edit=get_callback_var(callback_data, 'reply', bool)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_QUERY), state='*')
        async def edit_query(query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext) -> None:
            await store_notification_id(state, callback_data)
            await States.EDIT_QUERY.set()
            await overwrite_or_answer(query.message, messages.query_instructions())

        @dispatcher.message_handler(regexp=QUERY_PATTERN, state=States.EDIT_QUERY)
        async def process_edit_query(message: Message, state: FSMContext) -> None:
            notification = await get_notification(state)
            notification.query = message.text
            await SQLiteNotifications().upsert_model(notification)

            await finish_state(state)
            await overwrite_or_answer(
                message,
                messages.query_updated(notification),
                reply_markup=keyboards.notification_commands(notification)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_MIN_PRICE), state='*')
        async def edit_min_price(
                query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext
        ) -> None:
            await store_notification_id(state, callback_data)
            await States.EDIT_MIN_PRICE.set()
            await overwrite_or_answer(query.message, messages.price_instructions('Min'))

        @dispatcher.message_handler(regexp=PRICE_PATTERN, state=States.EDIT_MIN_PRICE)
        @dispatcher.message_handler(commands=Commands.REMOVE, state=States.EDIT_MIN_PRICE)
        async def process_edit_min_price(message: Message, state: FSMContext) -> None:
            price = message.text
            if price == f'/{Commands.REMOVE}':
                price = '0'

            notification = await get_notification(state)

            notification.min_price = round(float(price.replace(',', '.')))
            await SQLiteNotifications().upsert_model(notification)

            await overwrite_or_answer(
                message,
                messages.query_updated(notification),
                keyboards.notification_commands(notification)
            )

            await state.finish()

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_MAX_PRICE), state='*')
        async def edit_max_price(
                query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext
        ) -> None:
            await store_notification_id(state, callback_data)
            await States.EDIT_MAX_PRICE.set()
            await overwrite_or_answer(query.message, messages.price_instructions('Max'))

        @dispatcher.message_handler(regexp=PRICE_PATTERN, state=States.EDIT_MAX_PRICE)
        @dispatcher.message_handler(commands=Commands.REMOVE, state=States.EDIT_MAX_PRICE)
        async def process_edit_max_price(message: Message, state: FSMContext) -> None:
            price = message.text
            if price == f'/{Commands.REMOVE}':
                price = '0'

            notification = await get_notification(state)
            notification.max_price = round(float(price.replace(',', '.')))
            await SQLiteNotifications().upsert_model(notification)

            await overwrite_or_answer(
                message,
                messages.query_updated(notification),
                keyboards.notification_commands(notification)
            )

            await state.finish()

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.TOGGLE_ONLY_HOT))
        async def toggle_only_hot(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await get_notification(callback_data)
            notification.search_only_hot = not notification.search_only_hot
            await SQLiteNotifications().upsert_model(notification)

            await show_notification(query, callback_data)

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.TOGGLE_SEARCH_DESCR))
        async def toggle_search_description(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await get_notification(callback_data)
            notification.search_description = not notification.search_description
            await SQLiteNotifications().upsert_model(notification)

            await show_notification(query, callback_data)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_MYDEALZ))
        async def toggle_mydealz(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(get_chat_id(query), UColumns.SEARCH_MYDEALZ)
            await settings(query)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_MINDSTAR))
        async def toggle_mindstar(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(get_chat_id(query), UColumns.SEARCH_MINDSTAR)
            await settings(query)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_PREISJAEGER))
        async def toggle_preisjaeger(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(get_chat_id(query), UColumns.SEARCH_PREISJAEGER)
            await settings(query)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_IMAGES))
        async def toggle_images(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(get_chat_id(query), UColumns.SEND_IMAGES)
            await settings(query)

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.DELETE))
        async def delete_notification(
                query: CallbackQuery,
                callback_data: dict[str, Any]
        ) -> None:
            notification = await get_notification(callback_data)
            await SQLiteNotifications().delete_by_id(notification.id)

            await overwrite_or_answer(
                telegram_object=query.message,
                text=messages.notification_deleted(notification),
                reply_markup=keyboards.home_button(),
                reply_instead_of_edit=get_callback_var(callback_data, 'reply', bool)
            )

        @dispatcher.message_handler(regexp=QUERY_PATTERN_LIMITED_CHARS)
        async def add_notification_inconclusive(message: Message) -> None:
            text = message.text
            await overwrite_or_answer(
                message,
                messages.add_notification_inconclusive(text),
                reply_markup=keyboards.add_notification_inconclusive(text)
            )

        @dispatcher.message_handler(commands=Commands.CANCEL, state='*')
        async def cancel(message: Message, state: FSMContext) -> None:
            if not await state.get_state():
                return
            try:
                notification = await get_notification(state)

            except NotificationNotFoundError:
                await start(message, state)
            else:
                await overwrite_or_answer(
                    message,
                    messages.notification_overview(notification),
                    reply_markup=keyboards.notification_commands(notification)
                )

            await finish_state(state)

        @dispatcher.message_handler(state=States.ADD_NOTIFICATION)
        @dispatcher.message_handler(state=States.EDIT_QUERY)
        async def invalid_query(message: Message) -> None:
            await overwrite_or_answer(message, messages.invalid_query())

        @dispatcher.message_handler(state=States.EDIT_MIN_PRICE)
        @dispatcher.message_handler(state=States.EDIT_MAX_PRICE)
        async def invalid_price(message: Message, state: FSMContext) -> None:
            price_type = 'Min' if await state.get_state() == States.EDIT_MIN_PRICE else 'Max'

            await overwrite_or_answer(message, messages.invalid_price(price_type))

        @dispatcher.errors_handler()
        async def error_handler(update: Update, error: Exception) -> bool:
            if isinstance(error, (NotificationNotFoundError, TooManyNotificationsError)):
                error_mapping = {
                    NotificationNotFoundError: messages.notification_not_found(),
                    TooManyNotificationsError: messages.too_many_notifications()
                }
                error_message = error_mapping.get(type(error), '')
                if update.callback_query:
                    await update.callback_query.message.edit_reply_markup(reply_markup=None)
                    await update.callback_query.message.reply(error_message)
                else:
                    await update.message.answer(error_message, reply_markup=None)

                return True

            logging.error('Update: %s\n\ncaused error: %s', update, error)
            await self.send_error(error, update)

            return True

        self.dispatcher = dispatcher

    async def send_deal(self, deal: DealModel, notification: NotificationModel) -> None:
        message = messages.deal_msg(deal, notification)
        keyboard = keyboards.deal_kb(deal.link, notification)
        try:
            if notification.send_image:
                try:
                    await self.bot.send_photo(
                        chat_id=notification.user_id,
                        photo=deal.image_url,
                        caption=message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard
                    )

                    return
                except TelegramAPIError:
                    pass

            await self.bot.send_message(
                chat_id=notification.user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
                # disable_web_page_preview=True
            )
        except (Unauthorized, ChatNotFound):
            logging.info('User %s blocked the bot. Disable him', notification.user_id)
            await SQLiteUser().set_user_state(notification.user_id, False)

        except Exception as error:  # pylint: disable=broad-exception-caught
            await self.send_error(error, message=message)

    async def send_error(self,
                         error: Exception,
                         update: Update | None = None,
                         message: str | None = None
                         ) -> None:
        own_id = getenv('OWN_ID')

        if not own_id:
            return

        if message:
            error_message = \
                f'An exception was raised while sending following message:\n<pre>{html.escape(message)}</pre>'
        else:
            error_message = 'An exception was raised while handling an update\n'

            if update:
                error_message += \
                    f'<pre>update = {html.escape(json.dumps(update.to_python(), indent=2, ensure_ascii=False))}</pre>\n\n'

        tb_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        error_message += f'<pre>{html.escape(tb_string)}</pre>'

        if len(error_message) > 4096:
            for x in range(0, len(error_message), 4096):
                await self.bot.send_message(chat_id=own_id, text=error_message[x:x + 4096])
        else:
            await self.bot.send_message(chat_id=own_id, text=error_message)

    @classmethod
    async def shutdown(cls, dispatcher: Dispatcher) -> None:
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        executor.start_polling(self.dispatcher, loop=loop, on_shutdown=self.shutdown)
