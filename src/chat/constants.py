from enum import Enum, auto

VARIABLE_PATTERN = '!!{variable}={value}'


class Vars(str, Enum):
    NOTIFICATION_ID = auto()
    NOTIFICATION = auto()
    ADD_NOTIFICATION = auto()
    EDIT_NOTIFICATION = auto()
    DELETE_NOTIFICATION = auto()
    EDIT_QUERY = auto()
    EDIT_MAX_PRICE = auto()
    EDIT_MIN_PRICE = auto()
    SEARCH_ALL_DEALS = auto()
    ONLY_HOT_TOGGLE = auto()
    HOME = 'home'
    CANCEL = 'cancel'
