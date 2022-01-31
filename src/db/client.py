import logging
import sqlite3
from typing import Any, Dict, List

from src.config import Config
from src.db.constants import Columns, NColumns, Tables, UColumns

_COLUMN_CONFIG = {
    UColumns.USER_ID: 'INTEGER PRIMARY KEY',
    UColumns.USERNAME: 'TEXT',
    UColumns.FIRST_NAME: 'TEXT',
    UColumns.LAST_NAME: 'TEXT',
    NColumns.NOTIFICATION_ID: 'INTEGER PRIMARY KEY',
    NColumns.USER_ID: 'INTEGER NOT NULL',
    NColumns.QUERY: 'TEXT',
    NColumns.MIN_PRICE: 'INTEGER',
    NColumns.MAX_PRICE: 'INTEGER',
    NColumns.ONLY_HOT: 'BOOL',
    NColumns.SEARCH_MINDSTAR: 'BOOL',
}

_ADDITIONAL_COLUMN_CONFIG: Dict[Columns, str] = {
    NColumns.USER_ID: (
        f'FOREIGN KEY ({NColumns.USER_ID}) REFERENCES {Tables.USERS} ({UColumns.USER_ID}) '
        f'ON UPDATE CASCADE ON DELETE CASCADE'
    )
}


class SQLiteClient:
    def __init__(self) -> None:
        self.__conn: sqlite3.Connection = sqlite3.connect(Config.DATABASE)
        self.__c: sqlite3.Cursor = self.__conn.cursor()

    def commit(self) -> int:
        self.__conn.commit()

        return int(self.__c.lastrowid)

    def close(self) -> None:
        self.__conn.commit()
        self.__conn.close()

    def execute(self, query: str, *parameters: Any) -> sqlite3.Cursor:
        logging.debug('sqlite exec: %s', query)

        return self.__c.execute(query, parameters)

    def check_if_table_exists(self, table_name: Tables) -> bool:
        c = self.execute(f'SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{table_name}"')

        return c.fetchone()[0] == 1  # type: ignore

    def create_table(self, table_name: Tables, fields: List[Columns]) -> None:
        all_fields_query: List[str] = []
        additional_column_config: List[str] = []
        for field in fields:
            all_fields_query.append(f'{field} {_COLUMN_CONFIG[field]}')

            if field in _ADDITIONAL_COLUMN_CONFIG:
                additional_column_config.append(_ADDITIONAL_COLUMN_CONFIG[field])

        query = f'{", ".join(all_fields_query)}, {",".join(additional_column_config)}'.rstrip(', ')
        self.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({query});')

    def add_column(self, table_name: Tables, column: Columns) -> None:
        self.execute(f'ALTER TABLE {table_name} ADD {column} {_COLUMN_CONFIG[column]}')

    def get_all_columns(self, table_name: Tables) -> List[str]:
        c = self.execute(f'SELECT * FROM {table_name} LIMIT 1')

        return [description[0] for description in c.description]
