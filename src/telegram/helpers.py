from __future__ import annotations

from typing import Any, overload

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.exceptions import MessageCantBeEdited, MessageToEditNotFound, TelegramAPIError

from src.db.tables import SQLiteNotifications
from src.models import NotificationModel

CallbackDataType = dict[str, Any]


async def remove_reply_markup(
        telegram_object: Message | CallbackQuery
) -> None:
    message = telegram_object.message if isinstance(telegram_object, CallbackQuery) else telegram_object
    try:
        await message.edit_reply_markup(None)
    except TelegramAPIError:
        pass


async def overwrite_or_answer(
        telegram_object: Message | CallbackQuery,
        text: str,
        reply_markup: InlineKeyboardMarkup | None = None,
        reply_instead_of_edit: bool = False
) -> None:
    await remove_reply_markup(telegram_object)

    message = telegram_object.message if isinstance(telegram_object, CallbackQuery) else telegram_object

    try:
        if not reply_instead_of_edit:
            await message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

            return
    except (MessageCantBeEdited, MessageToEditNotFound):
        pass

    await message.answer(text, reply_markup=reply_markup, disable_web_page_preview=True)


async def store_notification_id(state: FSMContext, callback_data: CallbackDataType) -> None:
    async with state.proxy() as data:
        data['notification_id'] = callback_data['notification_id']


async def get_notification_id(telegram_object: CallbackDataType | FSMContext) -> int:
    if isinstance(telegram_object, FSMContext):
        async with telegram_object.proxy() as data:
            return int(data.get('notification_id', 0))

    return int(telegram_object.get('notification_id', 0))


async def get_notification(telegram_object: CallbackDataType | FSMContext) -> NotificationModel:
    return await SQLiteNotifications().get_by_id(
        await get_notification_id(telegram_object)
    )


def get_chat_id(telegram_object: Message | CallbackQuery) -> int:
    if isinstance(telegram_object, Message):
        return int(telegram_object.chat.id)

    return int(telegram_object.message.chat.id)


async def finish_state(state: FSMContext | None) -> None:
    if state and await state.get_state():
        await state.finish()


@overload
def get_callback_var(callback_data: dict[str, Any] | None, key: str, cast_type: type[bool]) -> bool:
    ...


@overload
def get_callback_var(callback_data: dict[str, Any] | None, key: str, cast_type: type[int]) -> int:
    ...


@overload
def get_callback_var(callback_data: dict[str, Any] | None, key: str, cast_type: type[str]) -> str:
    ...


def get_callback_var(
        callback_data: dict[str, Any] | None,
        key: str,
        cast_type: type[Any]
) -> bool | int | str:
    value: str = (callback_data or {}).get(key, '')

    if cast_type == bool:
        return value.lower() in {'1', 'true'}

    if cast_type == int:
        return int(value or 0)

    return value
