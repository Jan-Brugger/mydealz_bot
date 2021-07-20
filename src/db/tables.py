import logging
from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from src.db import columns as column
from src.db.client import SQLiteClient
from src.db.columns import COLUMN_CONFIG
from src.models import Model, NotificationModel, UserModel

TypeNotificationsRow = Tuple[int, int, str, int, int]
TypeUsersRow = Tuple[int, str, str, str]


class SQLiteTable(SQLiteClient):

    @property
    @abstractmethod
    def table_name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def table_columns(self) -> List[str]:
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def parse_row(cls, row: Tuple[Union[str, int], ...]) -> Model:
        raise NotImplementedError

    def init_table(self) -> None:
        if not self.check_if_table_exists(self.table_name):
            logging.info('Create table "%s"', self.table_name)
            self.create_table(self.table_name, self.table_columns)

        existing_column_names = self.get_all_columns(self.table_name)
        missing_column_names = set(self.table_columns).difference(existing_column_names)

        for missing_column in missing_column_names:
            logging.info('Add column "%s" to "%s"', missing_column, self.table_name)
            self.add_column(self.table_name, missing_column, COLUMN_CONFIG[missing_column])

    def upsert(self, update: Dict[str, Any], sqlite_id: int = 0) -> int:
        if sqlite_id:
            update.update({column.UID: sqlite_id})
        fields = ','.join(update.keys())

        self.execute(
            'INSERT OR REPLACE INTO `{}`({}) VALUES ({})'.format(
                self.table_name, fields, ','.join('?' * len(update.values()))
            ),
            *update.values()
        )
        return self.commit()

    def fetch_all(self, where: str = '') -> List[Tuple[Union[str, int], ...]]:
        where = ' WHERE {}'.format(where) if where else ''

        rows = self.execute('SELECT {fields} FROM {table}{where}'.format(
            fields=','.join(self.table_columns),
            table=self.table_name,
            where=where
        )).fetchall()

        if not isinstance(rows, list):
            raise Exception('Unexpected result')

        return rows

    def fetch_by_id(self, sqlite_id: int) -> Optional[Tuple[Union[str, int], ...]]:
        where_query = '{} == {}'.format(column.UID, sqlite_id)
        rows = self.fetch_all(where_query)

        return rows[0] if rows else None

    def fetch_by_field(self, field: str, value: Union[str, int]) -> List[Tuple[Union[str, int], ...]]:
        where_query = '{} == {}'.format(field, value)

        return self.fetch_all(where_query)

    def delete_by_id(self, sqlite_id: Union[str, int]) -> None:
        self.execute('DELETE FROM {} WHERE {}={}'.format(self.table_name, column.UID, sqlite_id))
        self.commit()

    def update(self, sqlite_id: int, field: str, new_value: Union[str, int]) -> None:
        self.execute(
            'UPDATE {table} SET {field} = "{value}" WHERE {id_col} = {sqlite_id}'.format(
                table=self.table_name,
                field=field,
                value=new_value,
                id_col=column.UID,
                sqlite_id=sqlite_id)
        )
        self.commit()


class SQLiteUser(SQLiteTable):
    table_name = 'users'
    table_columns = [column.UID, column.USERNAME, column.FIRST_NAME, column.LAST_NAME]

    @classmethod
    def parse_row(cls, row: Tuple[Union[str, int], ...]) -> UserModel:
        user = UserModel()
        user.id = int(row[cls.table_columns.index(column.UID)])
        user.username = str(row[cls.table_columns.index(column.USERNAME)])
        user.first_name = str(row[cls.table_columns.index(column.FIRST_NAME)])
        user.last_name = str(row[cls.table_columns.index(column.LAST_NAME)])

        return user

    def upsert_model(self, user: UserModel) -> None:
        update: Dict[str, str] = {
            column.USERNAME: user.username,
            column.FIRST_NAME: user.first_name,
            column.LAST_NAME: user.last_name
        }

        self.upsert(update, user.id)

    def get_by_id(self, sqlite_id: int) -> Optional[UserModel]:
        row = self.fetch_by_id(sqlite_id)
        return self.parse_row(row) if row else None


class SQLiteNotifications(SQLiteTable):
    table_name = 'notifications'
    table_columns = [column.UID, column.USER_ID, column.QUERY, column.MIN_PRICE, column.MAX_PRICE, column.ONLY_HOT]

    @classmethod
    def parse_row(cls, row: Tuple[Union[str, int], ...]) -> NotificationModel:
        notification = NotificationModel()
        notification.id = int(row[cls.table_columns.index(column.UID)])
        notification.user_id = int(row[cls.table_columns.index(column.USER_ID)])
        notification.query = str(row[cls.table_columns.index(column.QUERY)])
        notification.min_price = int(row[cls.table_columns.index(column.MIN_PRICE)] or 0)
        notification.max_price = int(row[cls.table_columns.index(column.MAX_PRICE)] or 0)
        notification.search_only_hot = str(row[cls.table_columns.index(column.ONLY_HOT)]) == 'True'

        return notification

    @classmethod
    def parse_rows(cls, rows: List[Tuple[Union[str, int], ...]]) -> List[NotificationModel]:
        result = []
        for row in rows:
            result.append(cls.parse_row(row))

        return result

    def upsert_model(self, notification: NotificationModel) -> int:
        update: Dict[str, Union[str, int, bool]] = {
            column.USER_ID: notification.user_id,
            column.QUERY: notification.query,
            column.MIN_PRICE: notification.min_price,
            column.MAX_PRICE: notification.max_price,
            column.ONLY_HOT: notification.search_only_hot,
        }

        return self.upsert(update, notification.id)

    def get_by_id(self, sqlite_id: int) -> Optional[NotificationModel]:
        row = self.fetch_by_id(sqlite_id)
        return self.parse_row(row) if row else None

    def get_by_user_id(self, user_id: int) -> List[NotificationModel]:
        rows = self.fetch_by_field(column.USER_ID, user_id)

        return self.parse_rows(rows)

    def get_all(self) -> List[NotificationModel]:
        rows: List[Tuple[Union[str, int], ...]] = self.fetch_all()

        return self.parse_rows(rows)
