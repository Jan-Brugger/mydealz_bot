import asyncio
import logging
from asyncio import create_task
from typing import List, Type

from src.bot import Bot
from src.core import Core
from src.db.tables import SQLiteNotifications
from src.feeds import AbstractFeed
from src.models import DealModel, NotificationModel


class Parser:
    @classmethod
    async def parse(cls) -> None:
        feeds: List[Type[AbstractFeed]] = AbstractFeed.__subclasses__()

        deals_list = await asyncio.gather(
            *[create_task(feed.get_new_deals()) for feed in feeds]
        )

        new_deals_amount = sum([len(deals) for deals in deals_list])
        if new_deals_amount == 0:
            return

        logging.info(
            'Found %s new deals (%s)', new_deals_amount,
            ' | '.join([f'{feeds[key].__name__}: {len(deals)}' for key, deals in enumerate(deals_list)])
        )

        for notification in SQLiteNotifications().get_all():
            for key, deals in enumerate(deals_list):
                if feeds[key].consider_deals(notification):
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
    asyncio.run(Parser().parse())
