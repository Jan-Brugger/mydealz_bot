import logging
import traceback
from contextlib import suppress

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent, Message

from src import config
from src.exceptions import NotificationNotFoundError
from src.telegram.messages import Messages

error_router = Router()

logger = logging.getLogger(__name__)


@error_router.error(ExceptionTypeFilter(NotificationNotFoundError))
async def notification_not_found(error: ErrorEvent) -> bool:
    if (callback_query := error.update.callback_query) and callback_query.message:
        message = callback_query.message
    elif error.update.message:
        message = error.update.message
    else:
        return False

    error_text = Messages.notification_not_found()

    if isinstance(message, Message):
        with suppress(TelegramAPIError):
            await message.delete_reply_markup()

        try:
            await message.edit_text(text=error_text)
        except TelegramAPIError:
            pass
        else:
            return True

    await message.answer(text=error_text)

    return True


@error_router.error()
async def send_error_event(error: ErrorEvent, bot: Bot) -> None:
    if not config.OWN_ID:
        return

    error_message = f"An exception was raised while handling an update ({error.update.update_id})"

    tb_list = traceback.format_exception(type(error.exception), error.exception, error.exception.__traceback__)
    error_message += f"\n\nTraceback:\n{''.join(tb_list)}"

    chars_per_message = 4096
    i = 0
    while i < len(error_message):
        await bot.send_message(chat_id=config.OWN_ID, text=error_message[i : i + chars_per_message])
        i += chars_per_message
