from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel
from src.telegram.constants import ADD_NOTIFICATION, DELETE_NOTIFICATION, EDIT_MAX_PRICE, EDIT_NOTIFICATION, EDIT_QUERY, \
    HOME, NOTIFICATION_ID, ONLY_HOT_TOGGLE, VARIABLE_PATTERN


def start(notifications: List[NotificationModel]) -> InlineKeyboardMarkup:
    keyboard = []
    for notification in sorted(notifications):
        id_suffix = VARIABLE_PATTERN.format(variable=NOTIFICATION_ID, value=notification.id)
        keyboard.append([
            InlineKeyboardButton('🔍 {}'.format(notification.query), callback_data=EDIT_NOTIFICATION + id_suffix)
        ])

    keyboard.append([InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=ADD_NOTIFICATION)])

    return InlineKeyboardMarkup(keyboard)


def notification_commands(notification: NotificationModel) -> InlineKeyboardMarkup:
    id_suffix = VARIABLE_PATTERN.format(variable=NOTIFICATION_ID, value=notification.id)
    # row 1
    keyboard = [[
        InlineKeyboardButton('✏️️ Suchbegriff ändern', callback_data=EDIT_QUERY + id_suffix),
        InlineKeyboardButton('💰 Maximalpreis ändern', callback_data=EDIT_MAX_PRICE + id_suffix)
    ]]

    # row 2
    if notification.search_only_hot:
        hot_toggle = InlineKeyboardButton('🆕 Alle Deals senden', callback_data=ONLY_HOT_TOGGLE + id_suffix)
    else:
        hot_toggle = InlineKeyboardButton('🌶️ Nur heiße Deals senden', callback_data=ONLY_HOT_TOGGLE + id_suffix)

    keyboard.append([
        hot_toggle,
        InlineKeyboardButton('❌ Löschen', callback_data=DELETE_NOTIFICATION + id_suffix),
    ])

    # row 3
    keyboard.append([
        InlineKeyboardButton('➕ Benachrichtigung hinzufügen', callback_data=ADD_NOTIFICATION),
        InlineKeyboardButton('🏠 Home', callback_data=HOME),
    ])

    return InlineKeyboardMarkup(keyboard)


def notification_deleted() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton('🏠 Home', callback_data=HOME)]])


def deal_kb(notification: NotificationModel) -> InlineKeyboardMarkup:
    id_suffix = VARIABLE_PATTERN.format(variable=NOTIFICATION_ID, value=notification.id)
    return InlineKeyboardMarkup([[
        InlineKeyboardButton('🗒️ Übersicht', callback_data=EDIT_NOTIFICATION + id_suffix),
        InlineKeyboardButton('❌ Löschen', callback_data=DELETE_NOTIFICATION + id_suffix),
        InlineKeyboardButton('🏠 Home', callback_data=HOME)
    ]])
