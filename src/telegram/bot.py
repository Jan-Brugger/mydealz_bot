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
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, ParseMode, ReplyKeyboardRemove, Update
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound, MessageCantBeEdited, Unauthorized

from src.config import Config
from src.db.constants import UColumns
from src.db.tables import SQLiteNotifications, SQLiteUser
from src.exceptions import NotificationNotFoundError, TooManyNotificationsError, UserNotFoundError
from src.models import DealModel, NotificationModel, UserModel
from src.telegram import keyboards, messages
from src.telegram.callbacks import ALLOWED_CHARACTERS, ALLOWED_SEPARATORS, Actions, AddNotificationCB, Commands, HomeCB, \
    NotificationCB, SettingsActions, SettingsCB, States

CallbackDataType = dict[str, Any]
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

        @dispatcher.message_handler(commands=Commands.START, state='*')
        @dispatcher.callback_query_handler(HomeCB.filter(), state='*')
        async def start(
                telegram_object: Message | CallbackQuery,
                state: FSMContext | None = None
        ) -> None:
            await __finish_state(state)

            sqlite_user = SQLiteUser()
            try:
                user = await __get_user(telegram_object)
            except UserNotFoundError:
                logging.info(
                    'User started the bot first time.\nUser: %s\nLocale:%s', telegram_object.from_user,
                    telegram_object.from_user.locale
                )
                user = UserModel().parse_telegram_object(telegram_object)
                logging.info('added user: %s', user.__dict__)
                await sqlite_user.upsert_model(user)

            notifications = await SQLiteNotifications().get_by_user_id(user.id)

            await __overwrite_or_answer(telegram_object, messages.start(user), keyboards.start(notifications))

        @dispatcher.message_handler(commands=Commands.HELP, state='*')
        async def help_handler(telegram_object: Message | CallbackQuery) -> None:
            await __overwrite_or_answer(
                telegram_object,
                messages.help_msg(),
                reply_markup=keyboards.home_button()
            )

        @dispatcher.message_handler(commands=Commands.SETTINGS, state='*')
        async def settings(
                telegram_object: Message | CallbackQuery,
                state: FSMContext | None = None
        ) -> None:
            await __finish_state(state)

            user = await __get_user(telegram_object)
            await __overwrite_or_answer(
                telegram_object,
                messages.settings(user),
                reply_markup=keyboards.settings(user)
            )

        @dispatcher.callback_query_handler(AddNotificationCB.filter(query=''))
        async def add_notification(query: CallbackQuery) -> None:
            await States.ADD_NOTIFICATION.set()
            await __overwrite_or_answer(query.message, messages.query_instructions())

        @dispatcher.message_handler(regexp=QUERY_PATTERN, state=States.ADD_NOTIFICATION)
        @dispatcher.callback_query_handler(AddNotificationCB.filter())
        async def process_add_notification(
                telegram_object: Message | CallbackQuery,
                state: FSMContext,
                callback_data: dict[str, Any] | None = None
        ) -> None:
            await state.finish()

            notification_query = callback_data.get('query', '') if callback_data else telegram_object.text
            chat_id = __get_chat_id(telegram_object)
            notification = await __save_notification(notification_query, chat_id)

            await __overwrite_or_answer(
                telegram_object,
                messages.notification_added(notification),
                reply_markup=keyboards.notification_commands(notification)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.VIEW))
        async def show_notification(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await __get_notification(callback_data)
            await __overwrite_or_answer(
                query.message,
                messages.notification_overview(notification),
                reply_markup=keyboards.notification_commands(notification)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_QUERY), state='*')
        async def edit_query(query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext) -> None:
            await __store_notification_id(state, callback_data)
            await States.EDIT_QUERY.set()
            await __overwrite_or_answer(query.message, messages.query_instructions())

        @dispatcher.message_handler(regexp=QUERY_PATTERN, state=States.EDIT_QUERY)
        async def process_edit_query(message: Message, state: FSMContext) -> None:
            notification = await __get_notification(state)
            notification.query = message.text
            await SQLiteNotifications().upsert_model(notification)

            await __finish_state(state)
            await __overwrite_or_answer(
                message,
                messages.query_updated(notification),
                reply_markup=keyboards.notification_commands(notification)
            )

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_MIN_PRICE), state='*')
        async def edit_min_price(
                query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext
        ) -> None:
            await __store_notification_id(state, callback_data)
            await States.EDIT_MIN_PRICE.set()
            await __overwrite_or_answer(query.message, messages.price_instructions('Min'))

        @dispatcher.message_handler(regexp=PRICE_PATTERN, state=States.EDIT_MIN_PRICE)
        @dispatcher.message_handler(commands=Commands.REMOVE, state=States.EDIT_MIN_PRICE)
        async def process_edit_min_price(message: Message, state: FSMContext) -> None:
            price = message.text
            if price == f'/{Commands.REMOVE}':
                price = '0'

            notification = await __get_notification(state)

            notification.min_price = round(float(price.replace(',', '.')))
            await SQLiteNotifications().upsert_model(notification)

            await __overwrite_or_answer(
                message,
                messages.query_updated(notification),
                keyboards.notification_commands(notification)
            )

            await state.finish()

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.UPDATE_MAX_PRICE), state='*')
        async def edit_max_price(
                query: CallbackQuery, callback_data: dict[str, Any], state: FSMContext
        ) -> None:
            await __store_notification_id(state, callback_data)
            await States.EDIT_MAX_PRICE.set()
            await __overwrite_or_answer(query.message, messages.price_instructions('Max'))

        @dispatcher.message_handler(regexp=PRICE_PATTERN, state=States.EDIT_MAX_PRICE)
        @dispatcher.message_handler(commands=Commands.REMOVE, state=States.EDIT_MAX_PRICE)
        async def process_edit_max_price(message: Message, state: FSMContext) -> None:
            price = message.text
            if price == f'/{Commands.REMOVE}':
                price = '0'

            notification = await __get_notification(state)
            notification.max_price = round(float(price.replace(',', '.')))
            await SQLiteNotifications().upsert_model(notification)

            await __overwrite_or_answer(
                message,
                messages.query_updated(notification),
                keyboards.notification_commands(notification)
            )

            await state.finish()

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.TOGGLE_ONLY_HOT))
        async def toggle_only_hot(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await __get_notification(callback_data)
            notification.search_only_hot = not notification.search_only_hot
            await SQLiteNotifications().upsert_model(notification)

            await show_notification(query, callback_data)

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.TOGGLE_SEARCH_DESCR))
        async def toggle_search_description(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await __get_notification(callback_data)
            notification.search_description = not notification.search_description
            await SQLiteNotifications().upsert_model(notification)

            await show_notification(query, callback_data)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_MYDEALZ))
        async def toggle_mydealz(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(__get_chat_id(query), UColumns.SEARCH_MYDEALZ)
            await settings(query)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_MINDSTAR))
        async def toggle_mindstar(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(__get_chat_id(query), UColumns.SEARCH_MINDSTAR)
            await settings(query)

        @dispatcher.callback_query_handler(SettingsCB.filter(action=SettingsActions.TOGGLE_PREISJAEGER))
        async def toggle_preisjaeger(query: CallbackQuery) -> None:
            await SQLiteUser().toggle_field(__get_chat_id(query), UColumns.SEARCH_PREISJAEGER)
            await settings(query)

        @dispatcher.callback_query_handler(NotificationCB.filter(action=Actions.DELETE))
        async def delete_notification(query: CallbackQuery, callback_data: dict[str, Any]) -> None:
            notification = await __get_notification(callback_data)
            await SQLiteNotifications().delete_by_id(notification.id)

            await __overwrite_or_answer(
                query.message,
                messages.notification_deleted(notification),
                reply_markup=keyboards.home_button()
            )

        @dispatcher.message_handler(regexp=QUERY_PATTERN_LIMITED_CHARS)
        async def add_notification_inconclusive(message: Message) -> None:
            text = message.text
            await __overwrite_or_answer(
                message,
                messages.add_notification_inconclusive(text),
                reply_markup=keyboards.add_notification_inconclusive(text)
            )

        @dispatcher.message_handler(commands=Commands.CANCEL, state='*')
        async def cancel(message: Message, state: FSMContext) -> None:
            if not await state.get_state():
                return
            try:
                notification = await __get_notification(state)

            except NotificationNotFoundError:
                await start(message, state)
            else:
                await __overwrite_or_answer(
                    message,
                    messages.notification_overview(notification),
                    reply_markup=keyboards.notification_commands(notification)
                )

            await __finish_state(state)

        @dispatcher.message_handler(state=States.ADD_NOTIFICATION)
        @dispatcher.message_handler(state=States.EDIT_QUERY)
        async def invalid_query(message: Message) -> None:
            await __overwrite_or_answer(message, messages.invalid_query())

        @dispatcher.message_handler(state=States.EDIT_MIN_PRICE)
        @dispatcher.message_handler(state=States.EDIT_MAX_PRICE)
        async def invalid_price(message: Message, state: FSMContext) -> None:
            price_type = 'Min' if await state.get_state() == States.EDIT_MIN_PRICE else 'Max'

            await __overwrite_or_answer(message, messages.invalid_price(price_type))

        @dispatcher.errors_handler()
        async def error_handler(update: Update, error: Exception) -> bool:

            if isinstance(error, (NotificationNotFoundError, TooManyNotificationsError)):
                error_mapping = {
                    NotificationNotFoundError: messages.notification_not_found(),
                    TooManyNotificationsError: messages.too_many_notifications()
                }
                error_message = error_mapping.get(type(error), '')
                if update.callback_query:
                    await update.callback_query.message.edit_text(error_message, reply_markup=None)
                else:
                    await update.message.answer(error_message, reply_markup=None)

                return True

            logging.error('Update: %s\n\ncaused error: %s', update, error)
            await self.send_error(error, update)

            return True

        async def __overwrite_or_answer(
                telegram_object: Message | CallbackQuery,
                text: str,
                reply_markup: InlineKeyboardMarkup | None = None
        ) -> None:
            message = telegram_object.message if isinstance(telegram_object, CallbackQuery) else telegram_object
            try:
                await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
            except MessageCantBeEdited:
                await message.answer(
                    text, reply_markup=reply_markup or ReplyKeyboardRemove(), disable_web_page_preview=True
                )

        async def __save_notification(query: str, chat_id: int) -> NotificationModel:
            amount_notifications = await SQLiteNotifications().count_notifications_by_user_id(chat_id)

            if amount_notifications >= Config.NOTIFICATION_CAP:
                raise TooManyNotificationsError(chat_id)

            notification = NotificationModel()
            notification.user_id = chat_id
            notification.query = query
            notification.id = await SQLiteNotifications().upsert_model(notification)

            logging.info('user %s added notification %s (%s)', notification.user_id, notification.id,
                         notification.query)

            return notification

        async def __store_notification_id(state: FSMContext, callback_data: CallbackDataType) -> None:
            async with state.proxy() as data:
                data['notification_id'] = callback_data['notification_id']

        async def __get_notification(source: CallbackDataType | FSMContext) -> NotificationModel:
            if isinstance(source, FSMContext):
                async with source.proxy() as data:
                    notification_id = data.get('notification_id', 0)
            else:
                notification_id = source.get('notification_id', 0)

            notification = await SQLiteNotifications().get_by_id(notification_id)
            if not notification:
                raise NotificationNotFoundError(notification_id)

            return notification

        def __get_chat_id(telegram_object: Message | CallbackQuery) -> int:
            if isinstance(telegram_object, Message):
                return int(telegram_object.chat.id)

            return int(telegram_object.message.chat.id)

        async def __get_user(source: Message | CallbackQuery) -> UserModel:
            user_id = __get_chat_id(source)
            user = await SQLiteUser().get_by_id(user_id)

            if not user:
                raise UserNotFoundError(user_id)

            return user

        async def __finish_state(state: FSMContext | None) -> None:
            if state and await state.get_state():
                await state.finish()

        self.dispatcher = dispatcher

    # pylint: disable=unused-argument
    async def send_deal(self, deal: DealModel, notification: NotificationModel, first_try: bool = True) -> None:
        try:
            await self.bot.send_message(
                chat_id=notification.user_id,
                text=messages.deal_msg(deal, notification),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.deal_kb(deal.link)
            )
            await self.bot.send_message(
                chat_id=notification.user_id,
                text=messages.edit_deal_msg(),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboards.edit_deal_kb(notification)
            )
        except (Unauthorized, ChatNotFound):
            logging.info('User %s blocked the bot. Remove all database entries', notification.user_id)
            await SQLiteUser().delete_by_id(notification.user_id)

        # except TimedOut as error:
        #     if first_try:
        #         logging.warning('Sending message timed out, try again.')
        #         self.send_deal(deal, notification, False)
        #     else:
        #         self.send_error(error)

        except Exception as error:
            await self.send_error(error)

    async def send_error(self, error: Exception, update: Update | None = None) -> None:
        own_id = getenv('OWN_ID')

        if not own_id:
            return

        message = 'An exception was raised while handling an update\n'
        if update:
            message += \
                f'<pre>update = {html.escape(json.dumps(update.to_python(), indent=2, ensure_ascii=False))}</pre>\n\n'

        tb_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        message += f'<pre>{html.escape(tb_string)}</pre>'

        if len(message) > 4096:
            for x in range(0, len(message), 4096):
                await self.bot.send_message(chat_id=own_id, text=message[x:x + 4096])
        else:
            await self.bot.send_message(chat_id=own_id, text=message)

    @classmethod
    async def shutdown(cls, dispatcher: Dispatcher) -> None:
        await dispatcher.storage.close()
        await dispatcher.storage.wait_closed()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        executor.start_polling(self.dispatcher, loop=loop, on_shutdown=self.shutdown)
