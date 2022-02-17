from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel, UserModel
from src.telegram.constants import CallbackVars, add_notification_cb


def start(notifications: List[NotificationModel]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for notification in sorted(notifications):

        query = f'🔍 {notification.query} '
        if notification.min_price:
            query += '💸'
        if notification.max_price:
            query += '💰'
        if notification.search_only_hot:
            query += '🌶️'

        keyboard.add(
            InlineKeyboardButton(
                query.strip(), callback_data=notification.get_callback(CallbackVars.VIEW)
            ),
        )

    keyboard.add(InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=CallbackVars.ADD))

    return keyboard


def notification_commands(notification: NotificationModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    keyboard.row(
        InlineKeyboardButton(
            '✏️️ Suchbegriff ändern', callback_data=notification.get_callback(CallbackVars.UPDATE_QUERY)
        ),
        InlineKeyboardButton('❌ Löschen', callback_data=notification.get_callback(CallbackVars.DELETE))
    )
    keyboard.row(
        InlineKeyboardButton(
            '💸 Minimalpreis ändern', callback_data=notification.get_callback(CallbackVars.UPDATE_MIN_PRICE)
        ),
        InlineKeyboardButton(
            '💰 Maximalpreis ändern', callback_data=notification.get_callback(CallbackVars.UPDATE_MAX_PRICE)
        )
    )

    hot_toggle_text = '🆕 Alle Deals senden' if notification.search_only_hot else '🌶️ Nur heiße Deals senden'

    keyboard.row(
        InlineKeyboardButton(hot_toggle_text, callback_data=notification.get_callback(CallbackVars.TOGGLE_ONLY_HOT)),
        InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=CallbackVars.ADD),
    )

    keyboard.row(
        InlineKeyboardButton('🏠 Home', callback_data=CallbackVars.HOME)
    )

    return keyboard


def deal_kb(notification: NotificationModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('🗒️ Übersicht', callback_data=notification.get_callback(CallbackVars.VIEW)),
        InlineKeyboardButton('❌ Löschen', callback_data=notification.get_callback(CallbackVars.DELETE)),
        InlineKeyboardButton('🏠 Home', callback_data=CallbackVars.HOME)
    )

    return keyboard


def add_notification_inconclusive(text: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✅ Ja', callback_data=add_notification_cb.new(query=text)),
        InlineKeyboardButton('❌ Nein', callback_data=CallbackVars.HOME)
    )

    return keyboard


def settings(user: UserModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    toggles = [
        (CallbackVars.TOGGLE_MYDEALZ, user.search_mydealz, 'mydealz.de'),
        (CallbackVars.TOGGLE_MINDSTAR, user.search_mindstar, 'MindStar'),
        (CallbackVars.TOGGLE_PREISJAEGER, user.search_preisjaeger, 'preisjaeger.at'),
    ]
    for toggle in toggles:
        keyboard.add(
            InlineKeyboardButton(f'✅ {toggle[2]}' if toggle[1] else f'❌ {toggle[2]}', callback_data=toggle[0])
        )

    keyboard.add(InlineKeyboardButton('🏠 Home', callback_data=CallbackVars.HOME))

    return keyboard
