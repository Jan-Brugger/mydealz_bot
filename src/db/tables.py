import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union

from src.db.client import RowType, SQLiteClient
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
    def _parse_row(self, row: RowType) -> Model:
        raise NotImplementedError

    def _parse_rows(self, rows: Iterable[RowType]) -> List[Model]:
        return [self._parse_row(row) for row in rows]

    async def _upsert(self, update: Dict[str, Any], sqlite_id: int = 0) -> int:
        if sqlite_id:
            update.update({'ROWID': sqlite_id})

        fields = ','.join(update.keys())
        values = tuple(int(v) if isinstance(v, bool) else v for v in update.values())

        return await self.update(
            f'INSERT OR REPLACE INTO `{self._table_name}`({fields}) VALUES ({",".join("?" * len(values))})',
            values
        )

    async def _fetch_all(self, where: str = '') -> List[Model]:
        query = self._base_query
        if where:
            query += f' WHERE {where}'
        rows = await self.fetch_all(query)

        return self._parse_rows(rows)

    async def _fetch_by_field(self, field: Columns, value: Union[str, int]) -> List[Model]:
        return await self._fetch_all(f'{self._table_name}.{field} == {value}')

    async def _fetch_by_id(self, sqlite_id: int) -> Optional[Model]:
        where_query = f'{self._table_name}.ROWID == {sqlite_id}'
        rows = await self._fetch_all(where_query)

        return rows[0] if rows else None

    async def delete_by_id(self, sqlite_id: Union[str, int]) -> None:
        await self.delete(f'DELETE FROM {self._table_name} WHERE {self._table_name}.ROWID == {sqlite_id}')

    async def toggle_field(self, sqlite_id: Union[str, int], field: Union[UColumns, NColumns]) -> None:
        await self.update(
            f'UPDATE {self._table_name} SET {field} = abs({field}-1) WHERE {self._table_name}.ROWID == {sqlite_id}'
            , None
        )

    async def init_table(self) -> None:
        if not await self.check_if_table_exists(self._table_name):
            logging.info('Create table "%s"', self._table_name)
            await self.create_table(self._table_name, self._columns)

        existing_column_names = await self.get_all_columns(self._table_name)

        for column in self._columns:
            if column in existing_column_names:
                existing_column_names.remove(column)
                continue

            logging.info('Add column "%s" to "%s"', column, self._table_name)
            await self.add_column(self._table_name, column)

        for deprecated_column in existing_column_names:
            logging.info('Remove deprecated column "%s" from "%s"', deprecated_column, self._table_name)
            await self.delete_column(self._table_name, deprecated_column)


class SQLiteUser(SQLiteTable):
    _table_name = Tables.USERS
    _columns = [col for col in UColumns]  # pylint: disable=unnecessary-comprehension
    _base_query = f'SELECT * FROM {_table_name}'

    def _parse_row(self, row: RowType) -> UserModel:
        user = UserModel()
        user.id = int(row[UColumns.USER_ID])  # type:ignore
        user.username = str(row[UColumns.USERNAME])
        user.first_name = str(row[UColumns.FIRST_NAME])
        user.last_name = str(row[UColumns.LAST_NAME])
        user.search_mydealz = bool(row[UColumns.SEARCH_MYDEALZ])
        user.search_mindstar = bool(row[UColumns.SEARCH_MINDSTAR])
        user.search_preisjaeger = bool(row[UColumns.SEARCH_PREISJAEGER])

        return user

    async def upsert_model(self, user: UserModel) -> None:
        update: Dict[str, Union[str, int]] = {
            UColumns.USER_ID: user.id,
            UColumns.USERNAME: user.username,
            UColumns.FIRST_NAME: user.first_name,
            UColumns.LAST_NAME: user.last_name,
            UColumns.SEARCH_MYDEALZ: user.search_mydealz,
            UColumns.SEARCH_MINDSTAR: user.search_mindstar,
            UColumns.SEARCH_PREISJAEGER: user.search_preisjaeger,
        }
        await self._upsert(update)

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        return await self._fetch_by_id(user_id)  # type: ignore


class SQLiteNotifications(SQLiteTable):
    _table_name = Tables.NOTIFICATIONS
    _columns = [col for col in NColumns]  # pylint: disable=unnecessary-comprehension
    _base_query = (
        f'SELECT * FROM {_table_name} '
        f'INNER JOIN {Tables.USERS} ON {Tables.USERS}.{UColumns.USER_ID}={Tables.NOTIFICATIONS}.{NColumns.USER_ID}'
    )

    def _parse_row(self, row: Dict[Union[NColumns, UColumns], Any]) -> NotificationModel:
        notification = NotificationModel()
        notification.id = int(row[NColumns.NOTIFICATION_ID])
        notification.user_id = int(row[NColumns.USER_ID])
        notification.query = str(row[NColumns.QUERY])
        notification.min_price = int(row[NColumns.MIN_PRICE] or 0)
        notification.max_price = int(row[NColumns.MAX_PRICE] or 0)
        notification.search_only_hot = bool(row[NColumns.ONLY_HOT])
        notification.search_mydealz = bool(row[UColumns.SEARCH_MYDEALZ])
        notification.search_mindstar = bool(row[UColumns.SEARCH_MINDSTAR])
        notification.search_preisjaeger = bool(row[UColumns.SEARCH_PREISJAEGER])

        return notification

    async def upsert_model(self, notification: NotificationModel) -> int:
        update: Dict[str, Union[str, int, bool]] = {
            NColumns.USER_ID: notification.user_id,
            NColumns.QUERY: notification.query,
            NColumns.MIN_PRICE: notification.min_price,
            NColumns.MAX_PRICE: notification.max_price,
            NColumns.ONLY_HOT: notification.search_only_hot,
        }

        return await self._upsert(update, notification.id)

    async def get_all(self) -> List[NotificationModel]:
        return await self._fetch_all()  # type: ignore

    async def get_by_id(self, sqlite_id: int) -> Optional[NotificationModel]:
        if not sqlite_id:
            return None

        return await self._fetch_by_id(sqlite_id)  # type: ignore

    async def get_by_user_id(self, user_id: int) -> List[NotificationModel]:
        return await self._fetch_by_field(NColumns.USER_ID, user_id)  # type: ignore
