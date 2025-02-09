from __future__ import annotations

from abc import ABC

from aiogram.filters.callback_data import CallbackData


class HomeCB(CallbackData, prefix="home"):
    page: int = 0
    reply: bool = False


class NewNotificationCB(CallbackData, prefix="new"):
    pass


class AddNotificationCB(CallbackData, prefix="add"):
    query: str


class EditNotificationCB(CallbackData, ABC, prefix=""):
    id: int


class UpdateQueryCB(EditNotificationCB, prefix="update_query"):
    pass


class ViewNotificationCB(EditNotificationCB, prefix="view"):
    reply: bool = False


class DeleteNotificationCB(EditNotificationCB, prefix="delete"):
    reply: bool = False


class UpdateMinPriceCB(EditNotificationCB, prefix="update_min_price"):
    pass


class UpdateMaxPriceCB(EditNotificationCB, prefix="update_max_price"):
    pass


class ToggleHotOnlyCB(EditNotificationCB, prefix="toggle_hot_only"):
    pass


class ToggleSearchDescriptionCB(EditNotificationCB, prefix="toggle_search_description"):
    pass


class ToggleSearchMydealz(CallbackData, prefix="toggle_mydealz"):
    pass


class ToggleSearchPreisjaeger(CallbackData, prefix="toggle_preisjaeger"):
    pass


class ToggleSendImages(CallbackData, prefix="toggle_images"):
    pass


class BroadcastCB(CallbackData, prefix="broadcast"):
    message_id: int
