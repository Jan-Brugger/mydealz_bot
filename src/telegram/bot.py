import asyncio
import html
import json
import logging
import os
import traceback
from os import getenv
from pickle import UnpicklingError
from time import sleep
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import PickleStorage
from aiogram.types import ParseMode, Update
from aiogram.utils import executor
from aiogram.utils.exceptions import ChatNotFound, Unauthorized

from src.config import Config
from src.db.tables import SQLiteUser
from src.exceptions import NotificationNotFoundError
from src.models import DealModel, NotificationModel
from src.telegram import keyboards, messages
from src.telegram.register import BOT_REGISTER, CBQRegister, MsgRegister


class TelegramBot:
    def __init__(self) -> None:
        self.bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
        try:
            storage = PickleStorage(path=Config.CHAT_FILE)
        except UnpicklingError:
            os.remove(Config.CHAT_FILE)
            sleep(3)
            storage = PickleStorage(path=Config.CHAT_FILE)

        dp = Dispatcher(self.bot, storage=storage)

        for handler in BOT_REGISTER:
            if isinstance(handler, MsgRegister):
                dp.register_message_handler(handler.function, *handler.args, **handler.kwargs)
            elif isinstance(handler, CBQRegister):
                dp.register_callback_query_handler(handler.function, *handler.args, **handler.kwargs)

        @dp.errors_handler()
        async def error_handler(update: Update, error: Exception) -> bool:
            if isinstance(error, NotificationNotFoundError):
                if update.callback_query:
                    await update.callback_query.message.edit_text(messages.notification_not_found(), reply_markup=None)
                else:
                    await update.message.answer(messages.notification_not_found(), reply_markup=None)

                return True

            logging.error('Update: %s\n\ncaused error: %s', update, error)
            await self.send_error(error, update)

            return True

        self.dp = dp

    # pylint: disable=unused-argument
    async def send_deal(self, deal: DealModel, notification: NotificationModel, first_try: bool = True) -> None:
        message = messages.deal_msg(deal, notification)
        keyboard = keyboards.deal_kb(notification)

        try:
            await self.bot.send_message(
                chat_id=notification.user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
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

        except Exception as error:  # pylint: disable=broad-except
            await self.send_error(error)

    async def send_error(self, error: Exception, update: Optional[Update] = None) -> None:
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
        executor.start_polling(self.dp, loop=loop, on_shutdown=self.shutdown)
