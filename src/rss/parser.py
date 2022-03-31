import asyncio
import logging
from asyncio import create_task
from typing import List, Type

from src.db.tables import SQLiteNotifications
from src.models import DealModel, NotificationModel
from src.rss.feeds import AbstractFeed
from src.telegram.bot import TelegramBot


class Parser:
    def __init__(self) -> None:
        self.bot = TelegramBot()

    async def run(self) -> None:
        try:
            await self.parse()
        except Exception as error:  # pylint: disable=broad-except
            await self.bot.send_error(error)

    async def parse(self) -> None:
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

        for notification in await SQLiteNotifications().get_all():
            for key, deals in enumerate(deals_list):
                if feeds[key].consider_deals(notification):
                    await self.search_for_matching_deals(notification, deals)

    async def search_for_matching_deals(self, notification: NotificationModel, deals: List[DealModel]) -> None:
        for deal in deals:
            if notification.min_price and (not deal.price.amount or deal.price.amount < notification.min_price):
                logging.debug('deal price (%s) is lower than searched min-price (%s) - skip',
                              deal.price.amount, notification.max_price)
                continue

            if deal.price.amount and notification.max_price and deal.price.amount > notification.max_price:
                logging.debug('deal price (%s) is higher than searched max-price (%s) - skip',
                              deal.price.amount, notification.max_price)
                continue

            logging.debug('search for query (%s) in title (%s)', notification.query, deal.title)

            title = ' '.join(deal.title.lower().split())
            for query in notification.queries:
                if all(x in title for x in query[0] if x) and not any(x in title for x in query[1] if x):
                    await self.bot.send_deal(deal, notification)
                    logging.info('searched query (%s) found in title (%s) - send deal', notification.query, deal.title)

                    break  # don't send same deal multiple times
