import asyncio
import logging
from abc import ABC, abstractmethod
from asyncio import create_task
from os.path import isfile
from time import mktime, struct_time
from typing import List, Type

import requests
from feedparser import FeedParserDict, parse

from src.bot import Bot
from src.config import Config
from src.core import Core
from src.db.tables import SQLiteNotifications
from src.models import DealModel, NotificationModel


class AbstractFeed(ABC):
    _last_update = 0.0
    _feed = ''

    @classmethod
    def get_last_update(cls) -> float:
        if cls._last_update:
            return cls._last_update

        if isfile(cls.last_update_file()):
            with open(cls.last_update_file(), 'r', encoding='utf-8') as last_update_file:
                return float(last_update_file.read() or 0)

        return 0

    @classmethod
    def set_last_update(cls, timestamp: float) -> None:
        if timestamp <= cls.get_last_update():
            return

        logging.debug('update last-update-timestamp from "%s" to "%s"', cls.get_last_update(), timestamp)

        cls._last_update = timestamp
        mode = 'r+' if isfile(cls.last_update_file()) else 'w'
        with open(cls.last_update_file(), mode, encoding='utf-8') as last_update_file:
            last_update_file.seek(0, 0)
            last_update_file.write(str(timestamp))
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
        latest_ts = 0.0

        deals = []
        for entry in feed['entries']:
            deal = cls.parse_deal(entry)
            if deal.title and deal.timestamp > last_update_ts:
                logging.debug('Added Deal with title "%s"', deal.title)
                deals.append(deal)
                latest_ts = max(latest_ts, deal.timestamp)

        logging.debug('Parsed %s, found %s new deals', cls._feed, len(deals))

        cls.set_last_update(latest_ts)

        return deals

    @classmethod
    async def get_new_deals(cls) -> List[DealModel]:
        try:
            response = requests.get(cls._feed, headers={'User-Agent': 'Telegram-Bot'}, timeout=10)

            return cls.parse_feed(response.content)

        except Exception as error:  # pylint: disable=broad-except
            logging.exception(error)
            Bot().send_error(error)

        return []

    @classmethod
    @abstractmethod
    def consider_deal(cls, notification: NotificationModel) -> bool:
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
        time = entry.get('published_parsed')
        if isinstance(time, struct_time):
            deal.timestamp = mktime(time)
        else:
            logging.error('RSS response is faulty. Expected struct_time, got %s', time)

        if deal.merchant and deal.merchant not in deal.title:
            deal.title = f'[{deal.merchant}] {deal.title}'

        return deal


class MyDealzAllFeed(MyDealzFeed, AbstractFeed):
    _last_update = 0.0
    _feed = 'https://www.mydealz.de/rss/alle'

    @classmethod
    def consider_deal(cls, notification: NotificationModel) -> bool:
        return not notification.search_only_hot


class MyDealzHotFeed(MyDealzFeed, AbstractFeed):
    _last_update = 0.0
    _feed = 'https://www.mydealz.de/rss/hot'  #

    @classmethod
    def consider_deal(cls, notification: NotificationModel) -> bool:
        return notification.search_only_hot


class MindStarsFeed(AbstractFeed):
    _last_update = 0.0
    _feed = 'https://www.mindfactory.de/xml/rss/mindstar_artikel.xml'

    @classmethod
    def parse_deal(cls, entry: FeedParserDict) -> DealModel:
        deal = DealModel()
        deal.merchant = 'Mindfactory'
        deal.title = f'[{deal.merchant}] {entry.get("title", "")}'
        deal.description = entry.get('summary', '')
        deal.price = float(entry.get('_price', '0').replace(',', ''))
        deal.link = entry.get('link', '')
        time = entry.get('published_parsed')
        if isinstance(time, struct_time):
            deal.timestamp = mktime(time)
        else:
            logging.error('RSS response is faulty. Expected struct_time, got %s', time)

        return deal

    @classmethod
    def consider_deal(cls, notification: NotificationModel) -> bool:
        return notification.search_mindstar


class Feed:
    @classmethod
    async def parse(cls) -> None:
        feeds: List[Type[AbstractFeed]] = AbstractFeed.__subclasses__()

        get_new_deal_tasks = []
        for feed in feeds:
            get_new_deal_tasks.append(create_task(feed.get_new_deals()))

        deals_list = await asyncio.gather(*get_new_deal_tasks)

        new_deals_amount = sum([len(deals) for deals in deals_list])
        if new_deals_amount == 0:
            return

        logging.info(
            'Found %s new deals (%s)', new_deals_amount,
            ' | '.join([f'{feeds[key].__name__}: {len(deals)}' for key, deals in enumerate(deals_list)])
        )

        for notification in SQLiteNotifications().get_all():
            for key, deals in enumerate(deals_list):
                if feeds[key].consider_deal(notification):
                    cls.search_for_matching_deals(notification, deals)

    @classmethod
    def search_for_matching_deals(cls, notification: NotificationModel, deals: List[DealModel]) -> None:
        for deal in deals:
            if notification.min_price and (not deal.price or deal.price < notification.min_price):
                logging.debug('deal price (%s) is lower than searched min-price (%s) - skip',
                              deal.price, notification.max_price)
                continue

            if deal.price and notification.max_price and deal.price > notification.max_price:
                logging.debug('deal price (%s) is higher than searched max-price (%s) - skip',
                              deal.price, notification.max_price)
                continue

            logging.debug('search for query (%s) in title (%s)', notification.query, deal.title)
            for comma_separated_query in notification.query.lower().split(','):
                logging.debug('')
                and_seperated_query = comma_separated_query.split('&')

                search_for = []
                exclude = []
                for query in and_seperated_query:
                    query = query.strip()
                    if query.startswith('!'):
                        exclude.append(query.lstrip('! '))
                    else:
                        search_for.append(query)

                if all(x in deal.title.lower() for x in search_for) \
                        and not any(x in deal.title.lower() for x in exclude):
                    Bot().send_deal(deal, notification)
                    logging.info('searched query (%s) found in title (%s) - send deal', notification.query, deal.title)

                    break  # don't send same deal multiple times


if __name__ == '__main__':
    Core.init()
    asyncio.run(Feed().parse())
