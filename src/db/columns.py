UID = 'uid'
USERNAME = 'username'
FIRST_NAME = 'first_name'
LAST_NAME = 'last_name'
USER_ID = 'user_id'
QUERY = 'query'
MIN_PRICE = 'min_price'
MAX_PRICE = 'max_price'
ONLY_HOT = 'hot_only'
SEARCH_MINDSTAR = 'search_mindstar'

COLUMN_CONFIG = {
    UID: 'INTEGER PRIMARY KEY AUTOINCREMENT',
    USERNAME: 'TEXT',
    FIRST_NAME: 'TEXT',
    LAST_NAME: 'TEXT',
    USER_ID: 'INTEGER',
    QUERY: 'TEXT',
    MIN_PRICE: 'INTEGER',
    MAX_PRICE: 'INTEGER',
    ONLY_HOT: 'BOOL',
    SEARCH_MINDSTAR: 'BOOL',
}
