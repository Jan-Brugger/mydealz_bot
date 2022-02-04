import logging
from abc import ABC, abstractmethod
from datetime import datetime
from os.path import isfile
from typing import List, Optional

import requests
from feedparser import FeedParserDict, parse
from requests import Timeout
from urllib3.exceptions import NewConnectionError

from src.config import Config
from src.models import DealModel, NotificationModel


class AbstractFeed(ABC):
    _last_update: Optional[datetime] = None
    _feed = ''

    @classmethod
    def get_last_update(cls) -> datetime:
        if cls._last_update:
            return cls._last_update

        if isfile(cls.last_update_file()):
            with open(cls.last_update_file(), 'r', encoding='utf-8') as last_update_file:
                file_content = last_update_file.read()
                try:
                    return datetime.fromisoformat(file_content)
                except ValueError:
                    return datetime.fromtimestamp(float(file_content))

        return datetime.min

    @classmethod
    def set_last_update(cls, last_update: datetime) -> None:
        if last_update <= cls.get_last_update():
            return

        logging.debug('update last-update from "%s" to "%s"', cls.get_last_update(), last_update)

        cls._last_update = last_update
        mode = 'r+' if isfile(cls.last_update_file()) else 'w'
        with open(cls.last_update_file(), mode, encoding='utf-8') as last_update_file:
            last_update_file.seek(0, 0)
            last_update_file.write(last_update.isoformat())
            last_update_file.close()

    @classmethod
    def last_update_file(cls) -> str:
        return f'{Config.FILE_DIR}/last_update_{cls.__name__}'

    @classmethod
    @abstractmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        pass

    @classmethod
    def parse_feed(cls, feed_content: bytes) -> List[DealModel]:
        feed = parse(feed_content)
        last_update_ts = cls.get_last_update()
        last_update = datetime.min

        deals = []
        for entry in feed['entries']:
            deal = cls.parse_deal(entry)
            if deal.title and deal.published > last_update_ts:
                logging.debug('Added Deal with title "%s"', deal.title)
                deals.append(deal)
                last_update = max(last_update, deal.published)

        logging.debug('Parsed %s, found %s new deals', cls._feed, len(deals))

        cls.set_last_update(last_update)

        return deals

    @classmethod
    async def get_new_deals(cls) -> List[DealModel]:
        try:
            response = requests.get(cls._feed, headers={'User-Agent': 'Telegram-Bot'}, timeout=30)
            return cls.parse_feed(response.content)

        except (Timeout, NewConnectionError):
            logging.error('Fetching %s timed out', cls._feed)

        return []

    @classmethod
    @abstractmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        pass


class MyDealzFeed(ABC):
    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.title = entry.get('title', '')
        deal.description = entry.get('description', '')
        deal.category = entry.get('category', '')
        deal.merchant = entry.get('pepper_merchant', {}).get('name', '')
        price = entry.get('pepper_merchant', {}).get('price', '').strip('€').replace('.', '').replace(',', '.')
        deal.price = float(price or 0)
        deal.link = entry.get('link', '')
        deal.published = datetime.strptime(entry.get('published'), '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
        if deal.merchant and deal.merchant not in deal.title:
            deal.title = f'[{deal.merchant}] {deal.title}'

        return deal


class MyDealzAllFeed(MyDealzFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.mydealz.de/rss/alle'

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return not notification.search_only_hot


class MyDealzHotFeed(MyDealzFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.mydealz.de/rss/hot'  #

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_only_hot


class MindStarsFeed(AbstractFeed):
    _last_update = None
    _feed = 'https://www.mindfactory.de/xml/rss/mindstar_artikel.xml'

    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.merchant = 'Mindfactory'
        deal.title = f'[{deal.merchant}] {entry.get("title", "")}'
        deal.description = entry.get('summary', '')
        deal.price = float(entry.get('_price', '0').replace(',', ''))
        deal.link = entry.get('link', '')
        deal.published = datetime.strptime(entry.get('published'), '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)

        return deal

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_mindstar
