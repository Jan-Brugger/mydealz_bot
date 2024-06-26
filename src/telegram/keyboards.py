from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel, UserModel
from src.telegram.callbacks import Actions, AddNotificationCB, BroadcastCB, HomeCB, NotificationCB, SettingsActions, \
    SettingsCB


def start(notifications: list[NotificationModel], page: int = 0) -> InlineKeyboardMarkup:
    notifications_per_page = 30

    i_start = notifications_per_page * page
    i_end = notifications_per_page * (page + 1)

    keyboard = InlineKeyboardMarkup()
    for notification in sorted(notifications)[i_start:i_end]:

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

    pagination = []
    if page:
        pagination.append(InlineKeyboardButton('<<', callback_data=HomeCB.new(page=page - 1)))
    if len(notifications) > i_end:
        pagination.append(InlineKeyboardButton('>>', callback_data=HomeCB.new(page=page + 1)))

    if pagination:
        keyboard.add(*pagination)

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
        InlineKeyboardButton('🏠 Home', callback_data=HomeCB.new(reply=True))
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
        (SettingsCB.new(action=SettingsActions.TOGGLE_PREISJAEGER), user.search_preisjaeger, 'preisjaeger.at'),
        (SettingsCB.new(action=SettingsActions.TOGGLE_IMAGES), user.send_images, 'Deal-Bilder'),
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


def broadcast_message(message_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('✅ Ja', callback_data=BroadcastCB.new(message_id=message_id)),
        InlineKeyboardButton('❌ Nein', callback_data=HomeCB.new())
    )

    return keyboard
