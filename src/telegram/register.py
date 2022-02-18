from abc import ABC
from typing import Any, Callable, Coroutine, Dict, Tuple

from src.telegram.constants import CallbackVars, Commands, States, add_notification_cb, notifications_cb
from src.telegram.handlers import Handlers

QUERY_PATTERN = r'^[\w\.+&,\! ]+$'
QUERY_PATTERN_LIMITED_CHARS = r'^[\w\.+&,\! ]{1,58}$'
PRICE_PATTERN = r'^\d+([,\.]\d{1,2})?$'


class AbstractRegister(ABC):
    def __init__(self, function: Callable[..., Coroutine[Any, Any, None]], *args: str, **kwargs: str):
        self.__function = function
        self.__args = args
        self.__kwargs = kwargs

    @property
    def function(self) -> Callable[..., Coroutine[Any, Any, None]]:
        return self.__function

    @property
    def args(self) -> Tuple[str, ...]:
        return self.__args

    @property
    def kwargs(self) -> Dict[str, str]:
        return self.__kwargs


class MsgRegister(AbstractRegister):
    pass


class CBQRegister(AbstractRegister):
    pass


BOT_REGISTER = [
    MsgRegister(Handlers.start, commands=Commands.START),
    MsgRegister(Handlers.help, commands=Commands.HELP),
    MsgRegister(Handlers.settings, commands=Commands.SETTINGS, state='*'),
    MsgRegister(Handlers.start_over, commands=Commands.START, state='*'),
    CBQRegister(Handlers.start_over, text=CallbackVars.HOME, state='*'),
    CBQRegister(Handlers.add_notification, text=CallbackVars.ADD),
    MsgRegister(Handlers.process_add_notification, regexp=QUERY_PATTERN, state=States.ADD_NOTIFICATION),
    CBQRegister(Handlers.show_notification, notifications_cb.filter(action=CallbackVars.VIEW)),
    CBQRegister(Handlers.edit_query, notifications_cb.filter(action=CallbackVars.UPDATE_QUERY), state='*'),
    MsgRegister(Handlers.process_edit_query, regexp=QUERY_PATTERN, state=States.EDIT_QUERY),
    CBQRegister(Handlers.edit_min_price, notifications_cb.filter(action=CallbackVars.UPDATE_MIN_PRICE), state='*'),
    MsgRegister(Handlers.process_edit_min_price, regexp=PRICE_PATTERN, state=States.EDIT_MIN_PRICE),
    MsgRegister(Handlers.process_edit_min_price, commands=Commands.REMOVE, state=States.EDIT_MIN_PRICE),
    CBQRegister(Handlers.edit_max_price, notifications_cb.filter(action=CallbackVars.UPDATE_MAX_PRICE), state='*'),
    MsgRegister(Handlers.process_edit_max_price, regexp=PRICE_PATTERN, state=States.EDIT_MAX_PRICE),
    MsgRegister(Handlers.process_edit_max_price, commands=Commands.REMOVE, state=States.EDIT_MAX_PRICE),
    CBQRegister(Handlers.toggle_only_hot, notifications_cb.filter(action=CallbackVars.TOGGLE_ONLY_HOT)),
    CBQRegister(Handlers.toggle_mydealz, text=CallbackVars.TOGGLE_MYDEALZ),
    CBQRegister(Handlers.toggle_mindstar, text=CallbackVars.TOGGLE_MINDSTAR),
    CBQRegister(Handlers.toggle_preisjaeger, text=CallbackVars.TOGGLE_PREISJAEGER),
    CBQRegister(Handlers.delete_notification, notifications_cb.filter(action=CallbackVars.DELETE)),
    MsgRegister(Handlers.add_notification_inconclusive, regexp=QUERY_PATTERN_LIMITED_CHARS),
    CBQRegister(Handlers.process_add_notification_inconclusive, add_notification_cb.filter()),
    MsgRegister(Handlers.cancel, commands=Commands.CANCEL, state='*'),
    MsgRegister(Handlers.invalid_query, state=States.ADD_NOTIFICATION),
    MsgRegister(Handlers.invalid_query, state=States.EDIT_QUERY),
    MsgRegister(Handlers.invalid_price, state=States.EDIT_MIN_PRICE),
    MsgRegister(Handlers.invalid_price, state=States.EDIT_MAX_PRICE),
]
