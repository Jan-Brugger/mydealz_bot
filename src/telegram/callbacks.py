from __future__ import annotations

from abc import ABCMeta
from enum import Enum, auto
from types import DynamicClassAttribute
from typing import Any

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData, CallbackDataFilter

ALLOWED_CHARACTERS = r'\w\!\[\]+-'
ALLOWED_SEPARATORS = r' &,'


class AbstractCallback(metaclass=ABCMeta):
    callback: CallbackData

    @classmethod
    def _create_callback_filter(cls, **kwargs: Any) -> CallbackDataFilter:
        return cls.callback.filter(**{k: v for k, v in kwargs.items() if v is not None})


class HomeCB(AbstractCallback):
    callback = CallbackData('home', 'reply')

    @classmethod
    def filter(cls) -> CallbackDataFilter:
        return cls._create_callback_filter()

    @classmethod
    def new(cls, reply: bool = False) -> str:
        return str(cls.callback.new(reply=reply))


class NotificationCB(AbstractCallback):
    callback = CallbackData('notification', 'action', 'notification_id', 'reply')

    @classmethod
    def filter(cls, action: Actions | None = None, notification_id: int | None = None) -> CallbackDataFilter:
        return cls._create_callback_filter(action=action, notification_id=notification_id)

    @classmethod
    def new(cls, action: Actions, notification_id: int, reply: bool = False) -> str:
        return str(cls.callback.new(action=action, notification_id=notification_id, reply=reply))


class SettingsCB(AbstractCallback):
    callback = CallbackData('settings', 'action')

    @classmethod
    def filter(cls, action: SettingsActions) -> CallbackDataFilter:
        return cls._create_callback_filter(action=action)

    @classmethod
    def new(cls, action: SettingsActions) -> str:
        return str(cls.callback.new(action=action))


class AddNotificationCB(AbstractCallback):
    callback = CallbackData('add', 'query')

    @classmethod
    def filter(cls, query: str | None = None) -> CallbackDataFilter:
        return cls._create_callback_filter(query=query)

    @classmethod
    def new(cls, query: str = '') -> str:
        return str(cls.callback.new(query=query))


class BroadcastCB(AbstractCallback):
    callback = CallbackData('broadcast', 'message_id')

    @classmethod
    def filter(cls) -> CallbackDataFilter:
        return cls._create_callback_filter(message_id=None)

    @classmethod
    def new(cls, message_id: int) -> str:
        return str(cls.callback.new(message_id=str(message_id)))


class StrEnum(str, Enum):
    @DynamicClassAttribute
    def value(self) -> str:
        return str(self._value_)  # pylint: disable=no-member


class Actions(StrEnum):
    VIEW = auto()
    UPDATE_QUERY = auto()
    DELETE = auto()
    UPDATE_MAX_PRICE = auto()
    UPDATE_MIN_PRICE = auto()
    TOGGLE_ONLY_HOT = auto()
    TOGGLE_SEARCH_DESCR = auto()


class SettingsActions(StrEnum):
    TOGGLE_MYDEALZ = auto()
    TOGGLE_MINDSTAR = auto()
    TOGGLE_PREISJAEGER = auto()
    TOGGLE_IMAGES = auto()


class Commands(StrEnum):
    CANCEL = 'cancel'
    REMOVE = 'remove'
    START = 'start'
    HELP = 'help'
    SETTINGS = 'settings'
    PING = 'ping'
    BROADCAST = 'broadcast'


class States(StatesGroup):
    ADD_NOTIFICATION = State()
    EDIT_QUERY = State()
    EDIT_MIN_PRICE = State()
    EDIT_MAX_PRICE = State()
    BROADCAST = State()
