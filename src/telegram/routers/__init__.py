from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InaccessibleMessage, InlineKeyboardMarkup, Message

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext


async def overwrite_or_answer(
    telegram_object: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
    *,
    reply_instead_of_edit: bool = False,
) -> None:
    message: Message | InaccessibleMessage
    if isinstance(telegram_object, Message):
        reply_instead_of_edit = True
        message = telegram_object
    elif telegram_object.message:
        message = telegram_object.message
    else:
        msg = "Message not found"
        raise ValueError(msg)

    if not reply_instead_of_edit and isinstance(message, Message):
        try:
            await message.edit_text(text, reply_markup=reply_markup)
        except TelegramBadRequest:
            pass
        else:
            return

    await message.answer(text, reply_markup=reply_markup)


async def store_id(state: FSMContext, notification_id: int) -> None:
    await state.update_data(data={"notification_id": notification_id})


async def get_id(state: FSMContext) -> int:
    try:
        return int((await state.get_data())["notification_id"])
    except KeyError as error:
        msg = "notification_id is missing. Did you clear state before try to get ID??"

        raise KeyError(msg) from error
