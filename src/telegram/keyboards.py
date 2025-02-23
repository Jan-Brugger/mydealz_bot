from collections.abc import Sequence

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.models import NotificationModel, UserModel
from src.telegram.callbacks import (
    AddNotificationCB,
    BroadcastCB,
    DeleteNotificationCB,
    HomeCB,
    NewNotificationCB,
    ToggleHotOnlyCB,
    ToggleSearchDescriptionCB,
    ToggleSearchMydealz,
    ToggleSearchPreisjaeger,
    ToggleSendImages,
    UpdateMaxPriceCB,
    UpdateMinPriceCB,
    UpdateQueryCB,
    ViewNotificationCB,
)


class Keyboards:
    @staticmethod
    def home_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text="🏠 Home", callback_data=HomeCB().pack())

    @staticmethod
    def start(
        notifications: Sequence[NotificationModel],
        page: int = 0,
    ) -> InlineKeyboardMarkup:
        notifications_per_page = 30

        i_start = notifications_per_page * page
        i_end = notifications_per_page * (page + 1)

        keyboard = []
        for notification in sorted(notifications)[i_start:i_end]:
            query = f"🔍 {notification.search_query} "
            if notification.min_price:
                query += "💸"
            if notification.max_price:
                query += "💰"
            if notification.search_hot_only:
                query += "🌶️"
            if notification.search_description:
                query += "🔎"

            keyboard.append(
                [InlineKeyboardButton(text=query, callback_data=ViewNotificationCB(id=notification.id).pack())]
            )

        pagination = []
        if page:
            pagination.append(
                InlineKeyboardButton(text="<<", callback_data=HomeCB(page=page - 1).pack()),
            )
        if len(notifications) > i_end:
            pagination.append(
                InlineKeyboardButton(text=">>", callback_data=HomeCB(page=page + 1).pack()),
            )

        if pagination:
            keyboard.append(pagination)

        keyboard.append(
            [
                InlineKeyboardButton(
                    text="➕ Suchbegriff hinzufügen",  # noqa: RUF001
                    callback_data=NewNotificationCB().pack(),
                )
            ]
        )

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def settings(user: UserModel) -> InlineKeyboardMarkup:
        def settings_text(text: str, *, cur_state: bool) -> str:
            return f"{'✅' if cur_state else '❌'} {text}"

        keyboard = [
            [
                InlineKeyboardButton(
                    text=settings_text("mydealz.de", cur_state=user.search_mydealz),
                    callback_data=ToggleSearchMydealz().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=settings_text("preisjaeger.at", cur_state=user.search_preisjaeger),
                    callback_data=ToggleSearchPreisjaeger().pack(),
                )
            ],
            [
                InlineKeyboardButton(
                    text=settings_text("Deal-Bilder", cur_state=user.send_images),
                    callback_data=ToggleSendImages().pack(),
                )
            ],
            [InlineKeyboardButton(text="🏠 Home", callback_data=HomeCB().pack())],
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def notification_commands(notification: NotificationModel) -> InlineKeyboardMarkup:
        hot_toggle_text = "🌶️ Nur heiße Deals" if notification.search_hot_only else "🆕 Alle Deals"
        search_descr_toggle_text = "🔍 Titel & Beschreibung" if notification.search_description else "🧐 Nur Titel"
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✏️️ Suchbegriff ändern", callback_data=UpdateQueryCB(id=notification.id).pack()
                ),
                InlineKeyboardButton(text="❌ Löschen", callback_data=DeleteNotificationCB(id=notification.id).pack()),
            ],
            [
                InlineKeyboardButton(
                    text="💸 Minimalpreis ändern", callback_data=UpdateMinPriceCB(id=notification.id).pack()
                ),
                InlineKeyboardButton(
                    text="💰 Maximalpreis ändern", callback_data=UpdateMaxPriceCB(id=notification.id).pack()
                ),
            ],
            [
                InlineKeyboardButton(text=hot_toggle_text, callback_data=ToggleHotOnlyCB(id=notification.id).pack()),
                InlineKeyboardButton(
                    text=search_descr_toggle_text, callback_data=ToggleSearchDescriptionCB(id=notification.id).pack()
                ),
            ],
            [
                InlineKeyboardButton(text="➕ Suchbegriff hinzufügen", callback_data=NewNotificationCB().pack()),  # noqa: RUF001
                InlineKeyboardButton(text="🏠 Home", callback_data=HomeCB().pack()),
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def add_notification_inconclusive(text: str) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Ja", callback_data=AddNotificationCB(query=text).pack()),
                InlineKeyboardButton(text="❌ Nein", callback_data=HomeCB().pack()),
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def deal_kb(deal_link: str, notification: NotificationModel) -> InlineKeyboardMarkup:
        keyboard = [
            [InlineKeyboardButton(text="Zum Deal", url=deal_link)],
            [
                InlineKeyboardButton(
                    text="🗒️ Übersicht",
                    callback_data=ViewNotificationCB(id=notification.id, reply=True).pack(),
                ),
                InlineKeyboardButton(
                    text="❌ Löschen",
                    callback_data=DeleteNotificationCB(id=notification.id, reply=True).pack(),
                ),
                InlineKeyboardButton(text="🏠 Home", callback_data=HomeCB(reply=True).pack()),
            ],
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def broadcast_message(message_id: int) -> InlineKeyboardMarkup:
        keyboard = [
            [
                InlineKeyboardButton(text="✅ Ja", callback_data=BroadcastCB(message_id=message_id).pack()),
                InlineKeyboardButton(text="❌ Nein", callback_data=HomeCB().pack()),
            ]
        ]

        return InlineKeyboardMarkup(inline_keyboard=keyboard)
