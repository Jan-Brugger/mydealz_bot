from __future__ import annotations

import asyncio
import contextlib
import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

import requests
from feedparser import FeedParserDict, parse
from price_parser import Price
from urllib3.exceptions import HTTPError

from src.config import Config
from src.models import DealModel, NotificationModel

logger = logging.getLogger(__name__)


class AbstractFeed(ABC):
    _last_update: datetime | None = None
    _feed = ''

    @classmethod
    def get_last_update(cls) -> datetime:
        if cls._last_update:
            return cls._last_update

        if Path.is_file(cls.last_update_file()):
            with Path.open(
                cls.last_update_file(),
                encoding='utf-8',
            ) as last_update_file:
                file_content = last_update_file.read()
                try:
                    return datetime.fromisoformat(file_content)
                except ValueError:
                    return datetime.fromtimestamp(float(file_content), tz=Config.TIMEZONE)

        return datetime.min.replace(tzinfo=Config.TIMEZONE)

    @classmethod
    def set_last_update(cls, last_update: datetime) -> None:
        if last_update <= cls.get_last_update():
            return

        logger.debug(
            'update last-update from "%s" to "%s"',
            cls.get_last_update(),
            last_update,
        )

        cls._last_update = last_update
        mode = 'r+' if Path.is_file(cls.last_update_file()) else 'w'
        with Path.open(cls.last_update_file(), mode, encoding='utf-8') as last_update_file:
            last_update_file.seek(0, 0)
            last_update_file.write(last_update.isoformat())
            last_update_file.close()

    @classmethod
    def last_update_file(cls) -> Path:
        return Path(f'{Config.FILE_DIR}/last_update_{cls.__name__}')

    @classmethod
    @abstractmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        pass

    @classmethod
    def parse_feed(cls, feed_content: bytes) -> list[DealModel]:
        feed = parse(feed_content)
        last_update_ts = cls.get_last_update()
        last_update = datetime.min.replace(tzinfo=Config.TIMEZONE)

        deals = []
        for entry in feed['entries']:
            deal = cls.parse_deal(entry)
            if deal.title and deal.published > last_update_ts:
                logger.debug('Added Deal with title "%s"', deal.title)
                deals.append(deal)
                last_update = max(last_update, deal.published)

        logger.debug('Parsed %s, found %s new deals', cls._feed, len(deals))

        cls.set_last_update(last_update)

        return deals

    @classmethod
    async def get_new_deals(cls) -> list[DealModel]:
        try:
            response = await asyncio.to_thread(
                requests.get, url=cls._feed, headers={'User-Agent': 'Telegram-Bot'}, timeout=30
            )

            return cls.parse_feed(response.content)

        except (OSError, HTTPError):
            logger.exception('Fetching %s failed.', cls._feed)

        return []

    @classmethod
    @abstractmethod
    def consider_deals(cls, notification: NotificationModel) -> bool:
        pass


class PepperFeed:
    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.title = entry.get('title', '')
        deal.category = entry.get('category', '')
        deal.merchant = entry.get('pepper_merchant', {}).get('name', '')
        deal.price = Price.fromstring(entry.get('pepper_merchant', {}).get('price', ''))
        deal.link = entry.get('link', '')

        try:
            deal.published = datetime.strptime(
                entry.get('published'),
                '%a, %d %b %Y %H:%M:%S %z',
            ).replace(tzinfo=None)
        except TypeError:
            logger.warning('Got invalid date: %s', entry)

        description = entry.get('summary', '')
        if description.startswith('<strong>'):
            # Remove price and merchant
            description = re.sub(r'<strong>.+?</strong>', '', description, count=1)
        deal.description = description

        with contextlib.suppress(KeyError, IndexError):
            deal.image_url = (entry['media_content'][0]['url']).replace(
                '150x150/qt/55',
                '768x768/qt/60',
            )

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
