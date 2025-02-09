from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, Chat, InlineKeyboardMarkup, Message

from src import config
from src.db.notification_client import NotificationClient
from src.db.user_client import UserClient
from src.exceptions import NotificationNotFoundError, UserNotFoundError
from src.models import UserModel
from src.telegram.callbacks import HomeCB
from src.telegram.enums import BotCommand
from src.telegram.keyboards import Keyboards
from src.telegram.messages import Messages
from src.telegram.routers import get_id, overwrite_or_answer

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

base_router: Router = Router()


@base_router.message(F.from_user.func(lambda from_user: config.WHITELIST and from_user.id not in config.WHITELIST))
async def not_whitelisted(message: Message, event_chat: Chat) -> None:
    UserClient().disable(event_chat.id)
    await message.answer(Messages.user_not_whitelisted())


@base_router.message(F.from_user.func(lambda from_user: config.BLACKLIST and from_user.id in config.BLACKLIST))
async def blacklisted(message: Message, event_chat: Chat) -> None:
    UserClient().disable(event_chat.id)
    await message.answer(Messages.user_blacklisted())


@base_router.message(CommandStart())
@base_router.callback_query(HomeCB.filter())
async def start(
    telegram_object: Message | CallbackQuery,
    event_chat: Chat,
    state: FSMContext,
    callback_data: HomeCB | None = None,
) -> None:
    await state.clear()
    user_client = UserClient()

    try:
        user = user_client.fetch(event_chat.id)
    except UserNotFoundError:
        user = UserModel(
            id=event_chat.id,
            username=event_chat.username,
            first_name=event_chat.first_name,
            last_name=event_chat.last_name,
        )
        logger.info("New user: %s", user)
        user_client.add(user)

    if not user.active:
        user_client.enable(user.id)

    notifications = NotificationClient().fetch_by_user_id(user.id)

    page = callback_data.page if callback_data else 0

    await overwrite_or_answer(
        telegram_object,
        text=Messages.start(user),
        reply_markup=Keyboards.start(notifications=notifications, page=page),
        reply_instead_of_edit=callback_data.reply if callback_data else False,
    )


@base_router.message(Command(BotCommand.HELP))
async def get_help(telegram_object: Message | CallbackQuery) -> None:
    await overwrite_or_answer(
        telegram_object,
        Messages.help_msg(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[Keyboards.home_button()]]),
    )


@base_router.message(Command(BotCommand.CANCEL))
async def cancel(message: Message, event_chat: Chat, state: FSMContext) -> None:
    try:
        notification_id = await get_id(state)
        notification = NotificationClient().fetch(notification_id)
    except (KeyError, NotificationNotFoundError):
        await start(telegram_object=message, event_chat=event_chat, state=state)
    else:
        await state.clear()

        await overwrite_or_answer(
            message,
            Messages.notification_overview(notification),
            reply_markup=Keyboards.notification_commands(notification),
        )
