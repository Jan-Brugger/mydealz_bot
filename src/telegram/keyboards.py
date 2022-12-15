from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel, UserModel
from src.telegram.callbacks import Actions, AddNotificationCB, HomeCB, NotificationCB, SettingsActions, SettingsCB


def start(notifications: list[NotificationModel]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for notification in sorted(notifications):

        query = f'🔍 {notification.query} '
        if notification.min_price:
            query += '💸'
        if notification.max_price:
            query += '💰'
        if notification.search_only_hot:
            query += '🌶️'
        if notification.search_description:
            query += '🔍'

        keyboard.add(
            InlineKeyboardButton(query.strip(), callback_data=NotificationCB.new(Actions.VIEW, notification.id))
        )

    keyboard.add(InlineKeyboardButton('➕ Suchbegriff hinzufügen', callback_data=AddNotificationCB.new()))

    return keyboard


def notification_commands(notification: NotificationModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton(
            '✏️️ Suchbegriff ändern', callback_data=NotificationCB.new(Actions.UPDATE_QUERY, notification.id)
        ),
        InlineKeyboardButton('❌ Löschen', callback_data=NotificationCB.new(Actions.DELETE, notification.id))
    )
    keyboard.row(
        InlineKeyboardButton(
            '💸 Minimalpreis ändern', callback_data=NotificationCB.new(Actions.UPDATE_MIN_PRICE, notification.id)
        ),
        InlineKeyboardButton(
            '💰 Maximalpreis ändern', callback_data=NotificationCB.new(Actions.UPDATE_MAX_PRICE, notification.id)
        )
    )

    hot_toggle_text = '🌶️ Nur heiße Deals' if notification.search_only_hot else '🆕 Alle Deals'

    keyboard.row(
        InlineKeyboardButton(
            hot_toggle_text, callback_data=NotificationCB.new(Actions.TOGGLE_ONLY_HOT, notification.id)
        ),
        InlineKeyboardButton('➕ Suchbegriff hinzufügen', callback_data=AddNotificationCB.new()),
    )

    search_descr_toggle_text = '🔍 Titel & Beschreibung' if notification.search_description else '🧐 Nur Titel'

    keyboard.row(
        InlineKeyboardButton(
            search_descr_toggle_text, callback_data=NotificationCB.new(Actions.TOGGLE_SEARCH_DESCR, notification.id)
        ),
        InlineKeyboardButton('🏠 Home', callback_data=HomeCB.new())
    )

    return keyboard


def deal_kb(deal_link: str, notification: NotificationModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('Zum Deal', url=deal_link),
    )
    keyboard.row(
        InlineKeyboardButton('🗒️ Übersicht', callback_data=NotificationCB.new(Actions.VIEW, notification.id, True)),
        InlineKeyboardButton('❌ Löschen', callback_data=NotificationCB.new(Actions.DELETE, notification.id, True)),
        InlineKeyboardButton('🏠 Home', callback_data=HomeCB.new(True))
    )

    return keyboard


def add_notification_inconclusive(text: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✅ Ja', callback_data=AddNotificationCB.new(query=text)),
        InlineKeyboardButton('❌ Nein', callback_data=HomeCB.new())
    )

    return keyboard


def settings(user: UserModel) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    toggles = [
        (SettingsCB.new(action=SettingsActions.TOGGLE_MYDEALZ), user.search_mydealz, 'mydealz.de'),
        (SettingsCB.new(action=SettingsActions.TOGGLE_MINDSTAR), user.search_mindstar, 'MindStar'),
        (SettingsCB.new(action=SettingsActions.TOGGLE_PREISJAEGER), user.search_preisjaeger, 'preisjaeger.at'),
    ]
    for toggle in toggles:
        keyboard.add(
            InlineKeyboardButton(f'✅ {toggle[2]}' if toggle[1] else f'❌ {toggle[2]}', callback_data=toggle[0])
        )

    keyboard.add(InlineKeyboardButton('🏠 Home', callback_data=HomeCB.new()))

    return keyboard


def home_button() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton('🏠 Home', callback_data=HomeCB.new())
    )

    return keyboard
