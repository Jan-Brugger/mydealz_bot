from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.filters import Command

from src.db.user_client import UserClient
from src.telegram.callbacks import ToggleSearchMydealz, ToggleSearchPreisjaeger, ToggleSendImages
from src.telegram.enums import BotCommand
from src.telegram.keyboards import Keyboards
from src.telegram.routers import overwrite_or_answer
from src.telegram.routers.base_router import base_router

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext
    from aiogram.types import CallbackQuery, Chat, Message

settings_router = Router()


@base_router.message(Command(BotCommand.SETTINGS))
async def settings(
    telegram_object: Message | CallbackQuery,
    event_chat: Chat,
    state: FSMContext,
) -> None:
    await state.clear()

    user = UserClient().fetch(event_chat.id)
    await overwrite_or_answer(
        telegram_object,
        "Einstellungen:",
        reply_markup=Keyboards.settings(user),
    )


@settings_router.callback_query(ToggleSearchMydealz.filter())
async def toggle_search_mydealz(
    callback_query: CallbackQuery,
    event_chat: Chat,
    state: FSMContext,
) -> None:
    UserClient().toggle_search_mydealz(event_chat.id)

    await settings(callback_query, event_chat, state)


@settings_router.callback_query(ToggleSearchPreisjaeger.filter())
async def toggle_search_preisjaeger(
    callback_query: CallbackQuery,
    event_chat: Chat,
    state: FSMContext,
) -> None:
    UserClient().toggle_search_preisjaeger(event_chat.id)

    await settings(callback_query, event_chat, state)


@settings_router.callback_query(ToggleSendImages.filter())
async def toggle_send_images(
    callback_query: CallbackQuery,
    event_chat: Chat,
    state: FSMContext,
) -> None:
    UserClient().toggle_send_images(event_chat.id)

    await settings(callback_query, event_chat, state)
