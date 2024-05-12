# pylint: disable=too-many-instance-attributes

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from aiogram.types import CallbackQuery, Message
from price_parser import Price

from src.telegram.callbacks import ALLOWED_CHARACTERS


class Model:
    pass


@dataclass
class UserModel(Model):
    def __init__(self) -> None:
        self.__id: int = 0
        self.__username: str = ''
        self.__first_name: str = ''
        self.__last_name: str = ''
        self.__search_mydealz: bool = True
        self.__search_preisjaeger: bool = False
        self.__send_images: bool = True
        self.__active: bool = True

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

    @property
    def search_mydealz(self) -> bool:
        return self.__search_mydealz

    @search_mydealz.setter
    def search_mydealz(self, value: bool) -> None:
        self.__search_mydealz = value

    @property
    def search_preisjaeger(self) -> bool:
        return self.__search_preisjaeger

    @search_preisjaeger.setter
    def search_preisjaeger(self, value: bool) -> None:
        self.__search_preisjaeger = value

    @property
    def send_images(self) -> bool:
        return self.__send_images

    @send_images.setter
    def send_images(self, value: bool) -> None:
        self.__send_images = value

    @property
    def active(self) -> bool:
        return self.__active

    @active.setter
    def active(self, value: bool) -> None:
        self.__active = value

    def parse_telegram_object(self, telegram_object: Message | CallbackQuery) -> UserModel:
        chat = telegram_object.message.chat if isinstance(telegram_object, CallbackQuery) else telegram_object.chat
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
        self.__search_description: bool = False
        self.__search_mydealz: bool = True
        self.__search_preisjaeger: bool = True
        self.__send_image: bool = True

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
        return self.__query.replace('&', ' & ').replace(',', ', ')

    @query.setter
    def query(self, value: str) -> None:
        value = (' '.join(value.split())).lower().replace('! ', '!')
        queries = re.findall(fr'([&,])?\s*(!?[{ALLOWED_CHARACTERS}]+)', value)

        self.__query = ''.join([f'{q[0] or "&"}{q[1]}' for q in queries]).strip('&, ')

    @property
    def queries(self) -> list[tuple[list[str], list[str]]]:
        """
        Returns a list of tuples where first element is list of include queries and second is list of exclude queries.

        :return: list of tuples where first element is list of include queries and second is list of exclude queries
        """
        queries = []

        or_queries = self.__query.split(',')
        for oq in or_queries:
            query: tuple[list[str], list[str]] = ([], [])
            for aq in oq.split('&'):
                aq = aq.strip().replace('+', ' ')
                if aq.startswith('!'):
                    query[1].append(aq[1:])
                else:
                    query[0].append(aq)

            queries.append(query)

        return queries

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
    def search_description(self) -> bool:
        return self.__search_description

    @search_description.setter
    def search_description(self, value: bool) -> None:
        self.__search_description = value

    @property
    def search_mydealz(self) -> bool:
        return self.__search_mydealz

    @search_mydealz.setter
    def search_mydealz(self, value: bool) -> None:
        self.__search_mydealz = value

    @property
    def search_preisjaeger(self) -> bool:
        return self.__search_preisjaeger

    @search_preisjaeger.setter
    def search_preisjaeger(self, value: bool) -> None:
        self.__search_preisjaeger = value

    @property
    def send_image(self) -> bool:
        return self.__send_image

    @send_image.setter
    def send_image(self, value: bool) -> None:
        self.__send_image = value


@dataclass
class DealModel(Model):
    def __init__(self) -> None:
        self.__title: str = ''
        self.__description: str = ''
        self.__category: str = ''
        self.__merchant: str = ''
        self.__price: Price = Price.fromstring('')
        self.__link: str = ''
        self.__image_url: str = ''
        self.__published: datetime = datetime.min

    @property
    def title(self) -> str:
        if not self.__merchant:
            return self.__title

        title = self.__title
        if title.lower().lstrip('[( ').startswith(self.__merchant.lower()):
            title = title[title.lower().find(self.__merchant.lower()) + len(self.__merchant):].lstrip(')] ')

        return f'[{self.merchant}] {title}'

    @title.setter
    def title(self, value: str) -> None:
        self.__title = ' '.join(value.split()).strip()

    @property
    def description(self) -> str:
        return self.__description

    @description.setter
    def description(self, value: str) -> None:
        self.__description = re.sub(re.compile(r'<.*?>'), ' ', value).strip()

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
    def price(self) -> Price:
        return self.__price

    @price.setter
    def price(self, value: Price) -> None:
        self.__price = value

    @property
    def link(self) -> str:
        return self.__link

    @link.setter
    def link(self, value: str) -> None:
        self.__link = value

    @property
    def image_url(self) -> str:
        return self.__image_url

    @image_url.setter
    def image_url(self, value: str) -> None:
        self.__image_url = value

    @property
    def published(self) -> datetime:
        return self.__published

    @published.setter
    def published(self, value: datetime) -> None:
        self.__published = value
