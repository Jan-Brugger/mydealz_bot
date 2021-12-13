import logging
import sqlite3
from typing import Any, List

from src.config import Config
from src.db.columns import COLUMN_CONFIG


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

    def check_if_table_exists(self, table_name: str) -> bool:
        c = self.execute(f'SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{table_name}"')
        return c.fetchone()[0] == 1  # type: ignore

    def create_table(self, table_name: str, fields: List[str]) -> None:
        all_fields_query = ''
        for field in fields:
            all_fields_query += f' {field} {COLUMN_CONFIG[field]},'

        self.execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({all_fields_query[:-1]});')

    def add_column(self, table_name: str, column_name: str, column_definition: str) -> None:
        self.execute(f'ALTER TABLE {table_name} ADD {column_name} {column_definition}')

    def get_all_columns(self, table_name: str) -> List[str]:
        c = self.execute(f'SELECT * FROM {table_name} LIMIT 1')
        return [description[0] for description in c.description]
