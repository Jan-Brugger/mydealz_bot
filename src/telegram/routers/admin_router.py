from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Bot, Router
from aiogram.exceptions import TelegramAPIError, TelegramMigrateToChat, TelegramNotFound, TelegramUnauthorizedError
from aiogram.filters import Command

from src import config
from src.db.db_client import DbClient
from src.db.user_client import UserClient
from src.telegram.callbacks import BroadcastCB
from src.telegram.enums import BotCommand
from src.telegram.keyboards import Keyboards
from src.telegram.messages import Messages
from src.telegram.routers import overwrite_or_answer
from src.telegram.states import States

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Message

admin_router = Router()

logger = logging.getLogger(__name__)


@admin_router.message(Command(BotCommand.BROADCAST))
async def broadcast(telegram_object: Message, state: FSMContext) -> None:
    await state.clear()
    if telegram_object.chat.id != config.OWN_ID:
        return

    await state.set_state(States.BROADCAST)
    await overwrite_or_answer(telegram_object, Messages.broadcast_start())


@admin_router.message(States.BROADCAST)
async def broadcast_validate(telegram_object: Message, state: FSMContext) -> None:
    await state.clear()
    await telegram_object.reply(
        text=Messages.broadcast_verify(),
        reply_markup=Keyboards.broadcast_message(telegram_object.message_id),
    )


@admin_router.callback_query(BroadcastCB.filter())
async def broadcast_send(
    telegram_object: CallbackQuery, callback_data: BroadcastCB, state: FSMContext, bot: Bot
) -> None:
    await state.clear()
    message_id = callback_data.message_id

    user_ids = UserClient.fetch_all_ids()

    sent_to = 0
    for user_id in user_ids:
        if await send_copy(bot, user_id, message_id):
            sent_to += 1

    await overwrite_or_answer(
        telegram_object,
        Messages.broadcast_sent(sent_to, len(user_ids)),
    )


async def send_copy(bot: Bot, user_id: int, message_id: int) -> bool:
    if not config.OWN_ID:
        msg = "Can't send broadcast without own ID in config"
        raise NotImplementedError(msg)

    try:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=config.OWN_ID,
            message_id=message_id,
            disable_notification=True,
        )
    except (TelegramUnauthorizedError, TelegramNotFound):
        logger.info("User %s blocked the bot. Disable him", user_id)
        UserClient.disable(user_id)
    except TelegramMigrateToChat as e:
        logger.info("Migrate user-id %s to %s", user_id, e.migrate_to_chat_id)
        DbClient.update_user_id(UserClient.fetch(user_id), e.migrate_to_chat_id)
    except TelegramAPIError:
        logger.exception("Failed to send broadcast-message")
    else:
        return True

    return False
