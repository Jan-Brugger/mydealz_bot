import logging
from time import mktime, struct_time
from typing import List

from feedparser import parse

from src.bot import Bot
from src.config import Config
from src.core import Core
from src.db.tables import SQLiteNotifications
from src.models import DealModel, NotificationModel


class Feed:
    FEED_ALL = 'https://www.mydealz.de/rss/alle'
    FEED_HOT = 'https://www.mydealz.de/rss/hot'

    @classmethod
    def parse(cls) -> None:
        notifications_hot = []
        notifications_all = []
        for notification in SQLiteNotifications().get_all():
            if notification.search_only_hot:
                notifications_hot.append(notification)
            else:
                notifications_all.append(notification)

        cls.notify(cls.FEED_ALL, notifications_all, Config.LAST_UPDATE_ALL)
        cls.notify(cls.FEED_HOT, notifications_hot, Config.LAST_UPDATE_HOT)

    @classmethod
    def notify(cls, feed: str, notifications: List[NotificationModel], last_update_file_path: str) -> None:
        last_update_file = open(last_update_file_path, 'r+')
        last_update_ts = float(last_update_file.read() or 0)

        entries = parse(feed)['entries']
        logging.debug('parsed feed %s, got %s entries', feed, len(entries))
        latest_ts = 0.0
        new_entries = 0

        for entry in entries:
            deal = cls.parse_entry(entry)
            if deal.timestamp <= float(last_update_ts):
                continue

            new_entries += 1
            if deal.timestamp > latest_ts:
                latest_ts = deal.timestamp

            for notification in notifications:
                if deal.price and notification.max_price and deal.price > notification.max_price:
                    logging.debug('deal price (%s) is higher than searched price (%s) - skip',
                                  deal.price, notification.max_price)
                    continue

                logging.debug('search for query (%s) in title (%s)', notification.query, deal.title)
                for query in notification.query.split(','):
                    logging.debug('')
                    if all(x.lower().strip() in deal.title.lower() for x in query.split('&')):
                        Bot().send_deal(deal, notification)
                        logging.info('searched query (%s) found in title (%s) - send deal',
                                     notification.query, deal.title)
                        break  # don't send same deal multiple times

        logging.info('parsed feed %s, got %s new entries', feed, new_entries)
        if latest_ts > last_update_ts:
            logging.info('update %s from %s to %s', last_update_file_path, last_update_ts, latest_ts)
            last_update_file.seek(0, 0)
            last_update_file.write(str(latest_ts))
            last_update_file.close()

    @classmethod
    def parse_entry(cls, entry: dict) -> DealModel:
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

        return deal


if __name__ == '__main__':
    Core.init()
    Feed().parse()
