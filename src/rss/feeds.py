from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from os.path import isfile

import requests
from feedparser import FeedParserDict, parse
from price_parser import Price
from urllib3.exceptions import HTTPError

from src.config import Config
from src.models import DealModel, NotificationModel


class AbstractFeed(ABC):
    _last_update: datetime | None = None
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
    def parse_feed(cls, feed_content: bytes) -> list[DealModel]:
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
    async def get_new_deals(cls) -> list[DealModel]:
        try:
            response = requests.get(cls._feed, headers={'User-Agent': 'Telegram-Bot'}, timeout=30)
            return cls.parse_feed(response.content)

        except (OSError, HTTPError) as error:
            logging.error('Fetching %s failed. Error: %s', cls._feed, error)

        return []

    @classmethod
    @abstractmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        pass


class PepperFeed(ABC):
    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.title = entry.get('title', '')
        deal.category = entry.get('category', '')
        deal.merchant = entry.get('pepper_merchant', {}).get('name', '')
        deal.price = Price.fromstring(entry.get('pepper_merchant', {}).get('price', ''))
        deal.link = entry.get('link', '')
        deal.published = datetime.strptime(entry.get('published'), '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)

        description = entry.get('summary', '')
        if description.startswith('<strong>'):
            # Remove price and merchant
            description = re.sub(r'<strong>.+?</strong>', '', description, 1)
        deal.description = description

        try:
            deal.image_url = (entry['media_content'][0]['url']).replace('150x150/qt/55', '768x768/qt/60')
        except (KeyError, IndexError):
            pass

        return deal


class MyDealzAllFeed(PepperFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.mydealz.de/rss/alle'

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_mydealz and not notification.search_only_hot


class MyDealzHotFeed(PepperFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.mydealz.de/rss/hot'

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_mydealz and notification.search_only_hot


class PreisjaegerAllFeed(PepperFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.preisjaeger.at/rss/alle'

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_preisjaeger and not notification.search_only_hot


class PreisjaegerHotFeed(PepperFeed, AbstractFeed):
    _last_update = None
    _feed = 'https://www.preisjaeger.at/rss/hot'

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_preisjaeger and notification.search_only_hot


class MindStarsFeed(AbstractFeed):
    _last_update = None
    _feed = 'https://www.mindfactory.de/xml/rss/mindstar_artikel.xml'

    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.merchant = 'Mindfactory'
        deal.title = entry.get('title', '')
        deal.description = entry.get('summary', '')
        deal.price = Price.fromstring(entry.get('_price', ''))
        deal.link = entry.get('link', '')
        deal.published = datetime.strptime(entry.get('published'), '%a, %d %b %Y %H:%M:%S %z').replace(tzinfo=None)
        deal.image_url = entry.get('_image', '')

        return deal

    @classmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        return notification.search_mindstar
