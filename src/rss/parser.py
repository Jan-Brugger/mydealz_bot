import asyncio
import logging
from asyncio import create_task

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
        except Exception as error:
            await self.bot.send_error(error)

    async def parse(self) -> None:
        feeds: list[type[AbstractFeed]] = AbstractFeed.__subclasses__()

        deals_list = await asyncio.gather(
            *[create_task(feed.get_new_deals()) for feed in feeds], return_exceptions=False
        )

        new_deals_amount = sum(len(deals) for deals in deals_list)
        if new_deals_amount == 0:
            return

        logging.info(
            'Found %s new deals (%s)', new_deals_amount,
            ' | '.join([f'{feeds[key].__name__}: {len(deals)}' for key, deals in enumerate(deals_list)])
        )

        all_notifications = await SQLiteNotifications().get_all()
        for feed_number, deals in enumerate(deals_list):
            for deal in deals:
                sent_to_users = []
                for notification in all_notifications:
                    if notification.user_id in sent_to_users or not feeds[feed_number].consider_deals(notification):
                        continue

                    if self.notification_matches_deal(notification, deal):
                        await self.bot.send_deal(deal, notification)
                        sent_to_users.append(notification.user_id)

    @classmethod
    def notification_matches_deal(cls, notification: NotificationModel, deal: DealModel) -> bool:
        if notification.min_price and (not deal.price.amount or deal.price.amount < notification.min_price):
            logging.debug('deal price (%s) is lower than searched min-price (%s) - skip',
                          deal.price.amount, notification.max_price)

            return False

        if deal.price.amount and notification.max_price and deal.price.amount > notification.max_price:
            logging.debug('deal price (%s) is higher than searched max-price (%s) - skip',
                          deal.price.amount, notification.max_price)

            return False

        logging.debug('search for query (%s) in title (%s)', notification.query, deal.title)

        title = ' '.join(deal.title.lower().split())
        title_and_description = title + ' '.join(deal.description.lower().split())
        for query in notification.queries:
            search_in = title_and_description if notification.search_description else title
            if all(x in search_in for x in query[0] if x) and not any(x in search_in for x in query[1] if x):
                logging.info('searched query (%s) found in (%s) - send deal', notification.query, search_in)

                return True

        return False
