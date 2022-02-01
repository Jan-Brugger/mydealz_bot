from enum import Enum

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData


class StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class CallbackVars(StrEnum):
    HOME = 'home'
    VIEW = 'view'
    ADD = 'add'
    DELETE = 'delete'
    UPDATE_QUERY = 'update_query'
    UPDATE_MIN_PRICE = 'update_min_price'
    UPDATE_MAX_PRICE = 'update_max_price'
    TOGGLE_ONLY_HOT = 'toggle_only_hot'
    TOGGLE_MINDSTAR = 'toggle_mindstar'


class Commands(StrEnum):
    CANCEL = 'cancel'
    REMOVE = 'remove'
    START = 'start'
    HELP = 'help'


class States(StatesGroup):
    ADD_NOTIFICATION = State()
    EDIT_QUERY = State()
    EDIT_MIN_PRICE = State()
    EDIT_MAX_PRICE = State()


notifications_cb = CallbackData('notification', 'action', 'notification_id')
add_notification_cb = CallbackData('add_notification', 'query')
