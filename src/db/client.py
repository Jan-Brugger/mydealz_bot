import logging
from sqlite3 import Row
from typing import Any, Awaitable, Callable, Dict, Iterable, List, Optional, Tuple, Union

import aiosqlite
from aiosqlite import Cursor

from src.config import Config
from src.db.constants import Columns, NColumns, Tables, UColumns

_COLUMN_CONFIG = {
    UColumns.USER_ID: 'INTEGER PRIMARY KEY',
    UColumns.USERNAME: 'TEXT',
    UColumns.FIRST_NAME: 'TEXT',
    UColumns.LAST_NAME: 'TEXT',
    UColumns.SEARCH_MYDEALZ: 'BOOL DEFAULT 1',
    UColumns.SEARCH_MINDSTAR: 'BOOL DEFAULT 1',
    UColumns.SEARCH_PREISJAEGER: 'BOOL DEFAULT 1',
    NColumns.NOTIFICATION_ID: 'INTEGER PRIMARY KEY',
    NColumns.USER_ID: 'INTEGER NOT NULL',
    NColumns.QUERY: 'TEXT',
    NColumns.MIN_PRICE: 'INTEGER',
    NColumns.MAX_PRICE: 'INTEGER',
    NColumns.ONLY_HOT: 'BOOL DEFAULT 0',
    NColumns.SEARCH_DESCRIPTION: 'BOOL DEFAULT 0',
}

_ADDITIONAL_COLUMN_CONFIG: Dict[Columns, str] = {
    NColumns.USER_ID: (
        f'FOREIGN KEY ({NColumns.USER_ID}) REFERENCES {Tables.USERS} ({UColumns.USER_ID}) '
        f'ON UPDATE CASCADE ON DELETE CASCADE'
    )
}

RowType = Dict[Union[UColumns, NColumns], Optional[Union[str, int]]]


class SQLiteClient:
    def __init__(self) -> None:
        self.__db = Config.DATABASE

    @staticmethod
    def dict_factory(cursor: Cursor, row: Tuple[Any, ...]) -> RowType:
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]

        return d

    async def __execute(
            self,
            query: str, values: Tuple[Union[str, int], ...] = (),
            callback_function: Optional[Callable[[Cursor], Awaitable[Any]]] = None
    ) -> Any:
        async with aiosqlite.connect(self.__db) as db:
            db.row_factory = self.dict_factory  # type:ignore
            cursor: Cursor = await db.execute(query, values)
            await db.commit()
            logging.debug('sqlite query executed successfully\nquery: %s\nvalues: %s', query, values)

            return await callback_function(cursor) if callback_function else cursor.lastrowid

    async def fetch_one(self, query: str) -> RowType:
        async def cb_func(cursor: Cursor) -> Optional[Row]: return await cursor.fetchone()

        return await self.__execute(query, callback_function=cb_func)  # type: ignore

    async def fetch_all(self, query: str) -> Iterable[RowType]:
        async def cb_func(cursor: Cursor) -> Iterable[Row]: return await cursor.fetchall()

        return await self.__execute(query, callback_function=cb_func)  # type: ignore

    async def fetch_description(self, query: str) -> Tuple[Tuple[Any, ...]]:
        async def cb_func(cursor: Cursor) -> Tuple[Tuple[Any, ...]]: return cursor.description

        return await self.__execute(query, callback_function=cb_func)  # type: ignore

    async def update(self, query: str, values: Optional[Tuple[Union[int, str], ...]]) -> int:
        return await self.__execute(query, values)  # type: ignore

    async def delete(self, query: str) -> None:
        async with aiosqlite.connect(self.__db) as db:
            await db.execute('PRAGMA foreign_keys=ON')
            await db.execute(query)
            await db.commit()

    async def check_if_table_exists(self, table_name: Tables) -> bool:
        entry = await self.fetch_one(
            f'SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{table_name}"'
        )

        return bool(entry and entry['count(name)'] == 1)  # type:ignore

    async def create_table(self, table_name: Tables, fields: List[Columns]) -> None:
        all_fields_query: List[str] = []
        additional_column_config: List[str] = []
        for field in fields:
            all_fields_query.append(f'{field} {_COLUMN_CONFIG[field]}')

            if field in _ADDITIONAL_COLUMN_CONFIG:
                additional_column_config.append(_ADDITIONAL_COLUMN_CONFIG[field])

        query = f'{", ".join(all_fields_query)}, {",".join(additional_column_config)}'.rstrip(', ')
        await self.__execute(f'CREATE TABLE IF NOT EXISTS {table_name} ({query});')

    async def add_column(self, table_name: Tables, column: Columns) -> None:
        await self.__execute(f'ALTER TABLE {table_name} ADD {column} {_COLUMN_CONFIG[column]}')

    async def delete_column(self, table_name: Tables, column: str) -> None:
        await self.__execute(f'ALTER TABLE {table_name} DROP {column}')

    async def get_all_columns(self, table_name: Tables) -> List[str]:
        description = await self.fetch_description(f'SELECT * FROM {table_name} LIMIT 1')

        return [description[0] for description in description]

    async def count_rows_by_field(self, table_name: Tables, field: Columns, value: Union[str, int]) -> int:
        async def cb_func(cursor: Cursor) -> Optional[Row]: return await cursor.fetchone()

        result = await self.__execute(
            f'SELECT COUNT(*) as counter FROM {table_name} WHERE {field} = {value}', callback_function=cb_func
        )

        return int(result.get('counter', 0))
