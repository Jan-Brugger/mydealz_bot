# pylint: disable=too-many-instance-attributes

from __future__ import annotations

from dataclasses import dataclass

from aiogram.types import Chat

from src.telegram.constants import notifications_cb


class Model:
    pass


@dataclass
class UserModel(Model):
    def __init__(self) -> None:
        self.__id: int = 0
        self.__username: str = ''
        self.__first_name: str = ''
        self.__last_name: str = ''

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        self.__id = value

    @property
    def username(self) -> str:
        return self.__username

    @username.setter
    def username(self, value: str) -> None:
        self.__username = value

    @property
    def first_name(self) -> str:
        return self.__first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        self.__first_name = value

    @property
    def last_name(self) -> str:
        return self.__last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        self.__last_name = value

    def parse_telegram_chat(self, chat: Chat) -> UserModel:
        self.id = chat.id
        self.username = chat.title or chat.username or ''
        self.first_name = chat.first_name or ''
        self.last_name = chat.last_name or ''

        return self


@dataclass
class NotificationModel(Model):
    def __init__(self) -> None:
        self.__id: int = 0
        self.__user_id: int = 0
        self.__query: str = ''
        self.__min_price: int = 0
        self.__max_price: int = 0
        self.__search_only_hot: bool = False
        self.__search_mindstar: bool = True

    def __lt__(self, other: NotificationModel) -> bool:
        return self.query.lower() < other.query.lower()

    @property
    def id(self) -> int:
        return self.__id

    @id.setter
    def id(self, value: int) -> None:
        self.__id = value

    @property
    def user_id(self) -> int:
        return self.__user_id

    @user_id.setter
    def user_id(self, value: int) -> None:
        self.__user_id = value

    @property
    def query(self) -> str:
        return self.__query

    @query.setter
    def query(self, value: str) -> None:
        self.__query = value

    @property
    def min_price(self) -> int:
        return self.__min_price

    @min_price.setter
    def min_price(self, value: int) -> None:
        self.__min_price = value

    @property
    def max_price(self) -> int:
        return self.__max_price

    @max_price.setter
    def max_price(self, value: int) -> None:
        self.__max_price = value

    @property
    def search_only_hot(self) -> bool:
        return self.__search_only_hot

    @search_only_hot.setter
    def search_only_hot(self, value: bool) -> None:
        self.__search_only_hot = value

    @property
    def search_mindstar(self) -> bool:
        return self.__search_mindstar

    @search_mindstar.setter
    def search_mindstar(self, value: bool) -> None:
        self.__search_mindstar = value

    def get_callback(self, action: str) -> str:
        return str(notifications_cb.new(notification_id=self.id, action=action))


@dataclass
class DealModel(Model):
    def __init__(self) -> None:
        self.__title: str = ''
        self.__description: str = ''
        self.__category: str = ''
        self.__merchant: str = ''
        self.__price: float = 0.0
        self.__link: str = ''
        self.__timestamp: float = 0.0

    @property
    def title(self) -> str:
        return self.__title

    @title.setter
    def title(self, value: str) -> None:
        self.__title = value

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = value

    @property
    def category(self) -> str:
        return self.__category

    @category.setter
    def category(self, value: str) -> None:
        self.__category = value

    @property
    def merchant(self) -> str:
        return self.__merchant

    @merchant.setter
    def merchant(self, value: str) -> None:
        self.__merchant = value

    @property
    def price(self) -> float:
        return self.__price

    @price.setter
    def price(self, value: float) -> None:
        self.__price = value

    @property
    def link(self) -> str:
        return self.__link

    @link.setter
    def link(self, value: str) -> None:
        self.__link = value

    @property
    def timestamp(self) -> float:
        return self.__timestamp

    @timestamp.setter
    def timestamp(self, value: float) -> None:
        self.__timestamp = value
