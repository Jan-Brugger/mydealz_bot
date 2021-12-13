from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel
from src.chat.constants import VARIABLE_PATTERN, Vars


def start(notifications: List[NotificationModel]) -> InlineKeyboardMarkup:
    keyboard = []
    for notification in sorted(notifications):
        id_suffix = VARIABLE_PATTERN.format(variable=Vars.NOTIFICATION_ID, value=notification.id)
        keyboard.append([
            InlineKeyboardButton(f'🔍 {notification.query}', callback_data=Vars.EDIT_NOTIFICATION + id_suffix)
        ])

    keyboard.append([InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=Vars.ADD_NOTIFICATION)])

    return InlineKeyboardMarkup(keyboard)


def notification_commands(notification: NotificationModel) -> InlineKeyboardMarkup:
    id_suffix = VARIABLE_PATTERN.format(variable=Vars.NOTIFICATION_ID, value=notification.id)

    if notification.search_only_hot:
        hot_toggle = InlineKeyboardButton('🆕 Alle Deals senden', callback_data=Vars.ONLY_HOT_TOGGLE + id_suffix)
    else:
        hot_toggle = InlineKeyboardButton('🌶️ Nur heiße Deals senden', callback_data=Vars.ONLY_HOT_TOGGLE + id_suffix)

    if notification.search_mindstar:
        mindstar_toggle = InlineKeyboardButton(
            '⭕ Mindstar nicht durchsuchen', callback_data=Vars.SEARCH_MINDSTAR_TOGGLE + id_suffix
        )
    else:
        mindstar_toggle = InlineKeyboardButton(
            '⭐ Mindstar durchsuchen', callback_data=Vars.SEARCH_MINDSTAR_TOGGLE + id_suffix
        )


    keyboard = [
        [
            InlineKeyboardButton('✏️️ Suchbegriff ändern', callback_data=Vars.EDIT_QUERY + id_suffix),
            InlineKeyboardButton('❌ Löschen', callback_data=Vars.DELETE_NOTIFICATION + id_suffix),
        ],
        [
            InlineKeyboardButton('💸 Minimalpreis ändern', callback_data=Vars.EDIT_MIN_PRICE + id_suffix),
            InlineKeyboardButton('💰 Maximalpreis ändern', callback_data=Vars.EDIT_MAX_PRICE + id_suffix),
        ],
        [
            hot_toggle,
            mindstar_toggle
        ],
        [
            InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=Vars.ADD_NOTIFICATION),
            InlineKeyboardButton('🏠 Home', callback_data=Vars.HOME),
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


def deal_kb(notification: NotificationModel) -> InlineKeyboardMarkup:
    id_suffix = VARIABLE_PATTERN.format(variable=Vars.NOTIFICATION_ID, value=notification.id)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('🗒️ Übersicht', callback_data=Vars.EDIT_NOTIFICATION + id_suffix),
        InlineKeyboardButton('❌ Löschen', callback_data=Vars.DELETE_NOTIFICATION + id_suffix),
        InlineKeyboardButton('🏠 Home', callback_data=Vars.HOME)
    ]])


def add_notification_inconclusive(text: str) -> InlineKeyboardMarkup:
    suffix = VARIABLE_PATTERN.format(variable=Vars.ADD_NOTIFICATION, value=text)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('✅ Ja', callback_data=Vars.ADD_NOTIFICATION + suffix),
        InlineKeyboardButton('❌ Nein', callback_data=Vars.CANCEL),
    ]])
