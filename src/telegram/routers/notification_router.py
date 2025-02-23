from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Chat, InlineKeyboardMarkup, Message

from src.db.notification_client import NotificationClient
from src.models import NotificationModel
from src.telegram.callbacks import (
    AddNotificationCB,
    DeleteNotificationCB,
    NewNotificationCB,
    ToggleHotOnlyCB,
    ToggleSearchDescriptionCB,
    UpdateMaxPriceCB,
    UpdateMinPriceCB,
    UpdateQueryCB,
    ViewNotificationCB,
)
from src.telegram.enums import BotCommand
from src.telegram.keyboards import Keyboards
from src.telegram.messages import Messages
from src.telegram.patterns import PRICE_PATTERN, QUERY_PATTERN, QUERY_PATTERN_LIMITED_CHARS
from src.telegram.routers import get_id, overwrite_or_answer, store_id
from src.telegram.states import States
from src.utils import is_valid_regex_query, prettify_query

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

notification_router: Router = Router()


@notification_router.callback_query(NewNotificationCB.filter())
async def new_notification(callback_query: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(States.ADD_NOTIFICATION)

    await overwrite_or_answer(
        callback_query,
        text=Messages.query_instructions(),
    )


@notification_router.message(States.ADD_NOTIFICATION, F.text.regexp(QUERY_PATTERN))
@notification_router.message(States.ADD_NOTIFICATION, F.text.func(is_valid_regex_query))
@notification_router.callback_query(AddNotificationCB.filter())
async def add_notification(
    telegram_object: Message | CallbackQuery,
    state: FSMContext,
    event_chat: Chat,
    callback_data: AddNotificationCB | None = None,
) -> None:
    await state.clear()

    if callback_data and callback_data.query:
        query = callback_data.query
    elif isinstance(telegram_object, Message) and telegram_object.text:
        query = telegram_object.text
    else:
        return

    notification = NotificationModel(search_query=prettify_query(query), user_id=event_chat.id)
    notification = NotificationClient().add(notification)

    await overwrite_or_answer(
        telegram_object,
        text=Messages.notification_added(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(ViewNotificationCB.filter())
async def show_notification(callback_query: CallbackQuery, callback_data: ViewNotificationCB) -> None:
    notification = NotificationClient().fetch(callback_data.id)

    await overwrite_or_answer(
        callback_query,
        Messages.notification_overview(notification),
        reply_markup=Keyboards.notification_commands(notification),
        reply_instead_of_edit=callback_data.reply,
    )


@notification_router.callback_query(UpdateQueryCB.filter())
async def update_query(
    callback_query: CallbackQuery,
    callback_data: UpdateQueryCB,
    state: FSMContext,
) -> None:
    await store_id(state, callback_data.id)
    await state.set_state(States.UPDATE_QUERY)
    await overwrite_or_answer(callback_query, Messages.query_instructions())


@notification_router.message(States.UPDATE_QUERY, F.text.regexp(QUERY_PATTERN))
@notification_router.message(States.UPDATE_QUERY, F.text.func(is_valid_regex_query))
async def process_update_query(message: Message, state: FSMContext) -> None:
    if not message.text:
        logger.error("Empty message text in process update should not be possible")
        return

    notification = NotificationClient().update_query(
        await get_id(state),
        prettify_query(message.text),
    )

    await state.clear()
    await overwrite_or_answer(
        message,
        Messages.query_updated(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(UpdateMinPriceCB.filter())
async def edit_min_price(
    callback_query: CallbackQuery,
    callback_data: UpdateMinPriceCB,
    state: FSMContext,
) -> None:
    await store_id(state, callback_data.id)
    await state.set_state(States.UPDATE_MIN_PRICE)
    await overwrite_or_answer(callback_query, Messages.price_instructions("Min"))


@notification_router.message(States.UPDATE_MIN_PRICE, F.text.regexp(PRICE_PATTERN))
@notification_router.message(States.UPDATE_MIN_PRICE, Command(BotCommand.REMOVE))
async def process_edit_min_price(message: Message, state: FSMContext) -> None:
    notification = NotificationClient().update_min_price(await get_id(state), __message_to_price(message.text))

    await state.clear()
    await overwrite_or_answer(
        message,
        Messages.query_updated(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(UpdateMaxPriceCB.filter())
async def edit_max_price(
    callback_query: CallbackQuery,
    callback_data: UpdateMaxPriceCB,
    state: FSMContext,
) -> None:
    await store_id(state, callback_data.id)
    await state.set_state(States.UPDATE_MAX_PRICE)
    await overwrite_or_answer(callback_query, Messages.price_instructions("Max"))


@notification_router.message(States.UPDATE_MAX_PRICE, F.text.regexp(PRICE_PATTERN))
@notification_router.message(States.UPDATE_MAX_PRICE, Command(BotCommand.REMOVE))
async def process_edit_max_price(message: Message, state: FSMContext) -> None:
    notification = NotificationClient().update_max_price(await get_id(state), __message_to_price(message.text))

    await state.clear()
    await overwrite_or_answer(
        message,
        Messages.query_updated(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(ToggleHotOnlyCB.filter())
async def toggle_only_hot(
    callback_query: CallbackQuery,
    callback_data: ToggleHotOnlyCB,
) -> None:
    notification = NotificationClient().toggle_search_hot_only(callback_data.id)

    await overwrite_or_answer(
        callback_query,
        Messages.notification_overview(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(ToggleSearchDescriptionCB.filter())
async def toggle_search_description(
    callback_query: CallbackQuery,
    callback_data: ToggleSearchDescriptionCB,
) -> None:
    notification = NotificationClient().toggle_search_description(callback_data.id)

    await overwrite_or_answer(
        callback_query,
        Messages.notification_overview(notification),
        reply_markup=Keyboards.notification_commands(notification),
    )


@notification_router.callback_query(DeleteNotificationCB.filter())
async def delete_notification(callback_query: CallbackQuery, callback_data: DeleteNotificationCB) -> None:
    notification = NotificationClient().delete(callback_data.id)

    await overwrite_or_answer(
        telegram_object=callback_query,
        text=Messages.notification_deleted(notification),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[Keyboards.home_button()]]),
        reply_instead_of_edit=callback_data.reply,
    )


@notification_router.message(States.UPDATE_QUERY)
@notification_router.message(States.ADD_NOTIFICATION)
async def invalid_query(message: Message) -> None:
    await overwrite_or_answer(message, Messages.invalid_query())


@notification_router.message(States.UPDATE_MIN_PRICE)
@notification_router.message(States.UPDATE_MAX_PRICE)
async def invalid_price(message: Message, state: FSMContext) -> None:
    price_type = "Min" if await state.get_state() == States.UPDATE_MIN_PRICE else "Max"

    await overwrite_or_answer(message, Messages.invalid_price(price_type))


def __message_to_price(price_str: str | None) -> int:
    if not price_str or price_str == f"/{BotCommand.REMOVE}":
        price_str = "0"

    return int(float(price_str.replace(",", ".")))


@notification_router.message(F.text.regexp(QUERY_PATTERN_LIMITED_CHARS))
@notification_router.message(F.text.func(is_valid_regex_query))
async def add_notification_inconclusive(message: Message) -> None:
    if not message.text:
        logger.error("Empty message text in inconclusive update should not be possible")
        return

    await overwrite_or_answer(
        message,
        Messages.add_notification_inconclusive(message.text),
        reply_markup=Keyboards.add_notification_inconclusive(message.text),
    )
