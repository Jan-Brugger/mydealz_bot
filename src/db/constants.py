from enum import Enum


class Tables(str, Enum):
    USERS = 'users'
    NOTIFICATIONS = 'notifications'


class Columns(str, Enum):
    pass


class UColumns(Columns):
    USER_ID = 'u_id'
    USERNAME = 'username'
    FIRST_NAME = 'first_name'
    LAST_NAME = 'last_name'
    SEARCH_MYDEALZ = 'search_md'
    SEARCH_MINDSTAR = 'search_ms'
    SEARCH_PREISJAEGER = 'search_pj'
    ACTIVE = 'active'


class NColumns(Columns):
    NOTIFICATION_ID = 'n_id'
    QUERY = 'query'
    MIN_PRICE = 'min_price'
    MAX_PRICE = 'max_price'
    ONLY_HOT = 'hot_only'
    SEARCH_DESCRIPTION = 'search_descr'
    USER_ID = 'user_id'
