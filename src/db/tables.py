import logging
import sqlite3
from abc import ABC, abstractmethod
from os import path
from typing import Any, Dict, List, Optional, Tuple, Union

from telegram import Bot as TelegramBot

from src.config import Config
from src.db.client import SQLiteClient
from src.db.constants import Columns, NColumns, Tables, UColumns
from src.models import Model, NotificationModel, UserModel


class SQLiteTable(SQLiteClient, ABC):
    @property
    @abstractmethod
    def _table_name(self) -> Tables:
        raise NotImplementedError

    @property
    @abstractmethod
    def _columns(self) -> List[Columns]:
        raise NotImplementedError

    @property
    @abstractmethod
    def _base_query(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def _parse_row(self, row: Tuple[Union[str, int], ...]) -> Model:
        raise NotImplementedError

    def _parse_rows(self, rows: List[Tuple[Union[str, int], ...]]) -> List[Model]:
        return [self._parse_row(row) for row in rows]

    def _upsert(self, update: Dict[str, Any], sqlite_id: int = 0) -> int:
        if sqlite_id:
            update.update({'ROWID': sqlite_id})

        fields = ','.join(update.keys())
        values = [int(v) if isinstance(v, bool) else v for v in update.values()]

        self.execute(
            f'INSERT OR REPLACE INTO `{self._table_name}`({fields}) VALUES ({",".join("?" * len(values))})', *values
        )

        return self.commit()

    def _fetch_all(self, where: str = '') -> List[Model]:
        query = self._base_query
        if where:
            query += f' WHERE {where}'

        rows = self.execute(query).fetchall()

        if not isinstance(rows, list):
            raise Exception('Unexpected result')

        return self._parse_rows(rows)

    def _fetch_by_field(self, field: Columns, value: Union[str, int]) -> List[Model]:
        return self._fetch_all(f'{self._table_name}.{field} == {value}')

    def _fetch_by_id(self, sqlite_id: int) -> Optional[Model]:
        where_query = f'{self._table_name}.ROWID == {sqlite_id}'
        rows = self._fetch_all(where_query)

        return rows[0] if rows else None

    def delete_by_id(self, sqlite_id: Union[str, int]) -> None:
        self.execute('PRAGMA foreign_keys=ON')
        self.execute(f'DELETE FROM {self._table_name} WHERE {self._table_name}.ROWID == {sqlite_id}')
        self.commit()

    def init_table(self) -> None:
        if not self.check_if_table_exists(self._table_name):
            logging.info('Create table "%s"', self._table_name)
            self.create_table(self._table_name, self._columns)

            # TODO REMOVE SOON pylint: disable=fixme
            if path.isfile(f'{Config.FILE_DIR}/sqlite.db'):
                self.migrate_old_db()

        existing_column_names = self.get_all_columns(self._table_name)
        for column in self._columns:
            if column in existing_column_names:
                continue

            logging.info('Add column "%s" to "%s"', column, self._table_name)
            self.add_column(self._table_name, column)

    # TODO REMOVE SOON pylint: disable=fixme
    def migrate_old_db(self) -> None:
        raise NotImplementedError


class SQLiteUser(SQLiteTable):
    _table_name = Tables.USERS
    _Columns_to_fetch = [UColumns.USER_ID, UColumns.USERNAME, UColumns.FIRST_NAME, UColumns.LAST_NAME, UColumns.BOT_ID]
    _base_query = f'SELECT {",".join(_Columns_to_fetch)} FROM {_table_name}'
    _columns = [col for col in UColumns]  # pylint: disable=unnecessary-comprehension

    def _parse_row(self, row: Tuple[Union[str, int], ...]) -> UserModel:
        user = UserModel()
        user.id = int(row[self._Columns_to_fetch.index(UColumns.USER_ID)])
        user.username = str(row[self._Columns_to_fetch.index(UColumns.USERNAME)])
        user.first_name = str(row[self._Columns_to_fetch.index(UColumns.FIRST_NAME)])
        user.last_name = str(row[self._Columns_to_fetch.index(UColumns.LAST_NAME)])
        user.bot_id = int(row[self._Columns_to_fetch.index(UColumns.BOT_ID)])

        return user

    def upsert_model(self, user: UserModel) -> None:
        update: Dict[str, Union[str, int]] = {
            UColumns.USER_ID: user.id,
            UColumns.USERNAME: user.username,
            UColumns.FIRST_NAME: user.first_name,
            UColumns.LAST_NAME: user.last_name,
            UColumns.BOT_ID: user.bot_id
        }
        self._upsert(update)

    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return self._fetch_by_id(user_id)  # type: ignore

    def get_bot_id(self, user_id: int) -> int:
        user = self.get_by_id(user_id)

        return user.bot_id if user else 0

    # TODO REMOVE SOON pylint: disable=fixme
    def migrate_old_db(self) -> None:
        rows = sqlite3.connect(f'{Config.FILE_DIR}/sqlite.db').cursor() \
            .execute('SELECT uid,username,first_name,last_name FROM users').fetchall()
        bot_id = int(TelegramBot(Config.BOT_TOKENS[0]).id)
        for row in rows:
            user = UserModel()
            user.id = int(row[0])
            user.username = row[1]
            user.first_name = row[2]
            user.last_name = row[3]
            user.bot_id = bot_id

            self.upsert_model(user)


class SQLiteNotifications(SQLiteTable):
    _table_name = Tables.NOTIFICATIONS
    _Columns_to_fetch = [NColumns.NOTIFICATION_ID, NColumns.QUERY, NColumns.MIN_PRICE, NColumns.MAX_PRICE,
                         NColumns.ONLY_HOT, NColumns.SEARCH_MINDSTAR, UColumns.BOT_ID, NColumns.USER_ID]
    _base_query = (
        f'SELECT {",".join(_Columns_to_fetch)} FROM {_table_name} '
        f'INNER JOIN {Tables.USERS} ON {Tables.USERS}.{UColumns.USER_ID}={Tables.NOTIFICATIONS}.{NColumns.USER_ID}'
    )
    _columns = [col for col in NColumns]  # pylint: disable=unnecessary-comprehension

    def _parse_row(self, row: Tuple[Union[str, int], ...]) -> NotificationModel:
        notification = NotificationModel()
        notification.id = int(row[self._Columns_to_fetch.index(NColumns.NOTIFICATION_ID)])
        notification.user_id = int(row[self._Columns_to_fetch.index(NColumns.USER_ID)])
        notification.query = str(row[self._Columns_to_fetch.index(NColumns.QUERY)])
        notification.min_price = int(row[self._Columns_to_fetch.index(NColumns.MIN_PRICE)] or 0)
        notification.max_price = int(row[self._Columns_to_fetch.index(NColumns.MAX_PRICE)] or 0)
        notification.search_only_hot = str(row[self._Columns_to_fetch.index(NColumns.ONLY_HOT)]) in ['True', '1']
        notification.search_mindstar = str(row[self._Columns_to_fetch.index(NColumns.SEARCH_MINDSTAR)]) in ['True', '1']
        notification.bot_id = int(row[self._Columns_to_fetch.index(UColumns.BOT_ID)] or 0)

        return notification

    def upsert_model(self, notification: NotificationModel) -> int:
        update: Dict[str, Union[str, int, bool]] = {
            NColumns.USER_ID: notification.user_id,
            NColumns.QUERY: notification.query,
            NColumns.MIN_PRICE: notification.min_price,
            NColumns.MAX_PRICE: notification.max_price,
            NColumns.ONLY_HOT: notification.search_only_hot,
            NColumns.SEARCH_MINDSTAR: notification.search_mindstar,
        }

        return self._upsert(update, notification.id)

    def get_all(self) -> List[NotificationModel]:
        return self._fetch_all()  # type: ignore

    def get_by_id(self, sqlite_id: int) -> Optional[NotificationModel]:
        return self._fetch_by_id(sqlite_id)  # type: ignore

    def get_by_user_id(self, user_id: int) -> List[NotificationModel]:
        return self._fetch_by_field(NColumns.USER_ID, user_id)  # type: ignore

    # TODO REMOVE SOON pylint: disable=fixme
    def migrate_old_db(self) -> None:
        rows = sqlite3.connect(f'{Config.FILE_DIR}/sqlite.db').cursor() \
            .execute('SELECT uid,user_id,query,min_price,max_price,hot_only,search_mindstar FROM notifications') \
            .fetchall()

        for row in rows:
            notification = NotificationModel()
            notification.id = int(row[0])
            notification.user_id = int(row[1])
            notification.query = str(row[2])
            notification.min_price = int(row[3] or 0)
            notification.max_price = int(row[4] or 0)
            notification.search_only_hot = str(row[5]) in ['True', '1']
            notification.search_mindstar = str(row[6]) in ['True', '1']

            self.upsert_model(notification)
