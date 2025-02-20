import asyncio
import logging
from asyncio import create_task

from src.db.notification_client import NotificationClient
from src.models import DealModel, NotificationModel
from src.rss.feeds import AbstractFeed
from src.telegram.bot import TelegramBot

logger = logging.getLogger(__name__)


class FeedParser:
    @classmethod
    async def run(cls) -> None:
        feeds: list[type[AbstractFeed]] = AbstractFeed.__subclasses__()

        deals_list = await asyncio.gather(
            *[create_task(feed.get_new_deals()) for feed in feeds],
            return_exceptions=False,
        )

        new_deals_amount = sum(len(deals) for deals in deals_list)

        logger.info(
            "Found %s new deals (%s)",
            new_deals_amount,
            " | ".join([f"{feeds[key].__name__}: {len(deals)}" for key, deals in enumerate(deals_list)]),
        )

        if new_deals_amount == 0:
            return

        all_notifications = NotificationClient().fetch_all_active()
        for feed_number, deals in enumerate(deals_list):
            for deal in deals:
                sent_to_users = []
                for notification, user in all_notifications:
                    if user.id in sent_to_users or not feeds[feed_number].consider_deals(notification, user):
                        continue

                    if cls.notification_matches_deal(notification, deal):
                        await TelegramBot.send_deal(deal, notification, user)
                        sent_to_users.append(notification.user_id)

    @classmethod
    def notification_matches_deal(
        cls,
        notification: NotificationModel,
        deal: DealModel,
    ) -> bool:
        if notification.min_price and (not deal.price.amount or deal.price.amount < notification.min_price):
            logger.debug(
                "deal price (%s) is lower than searched min-price (%s) - skip",
                deal.price.amount,
                notification.max_price,
            )

            return False

        if deal.price.amount and notification.max_price and deal.price.amount > notification.max_price:
            logger.debug(
                "deal price (%s) is higher than searched max-price (%s) - skip",
                deal.price.amount,
                notification.max_price,
            )

            return False

        search_text = deal.search_title_and_description if notification.search_description else deal.search_title

        if notification.queries.any_match(search_text):
            logger.info(
                "searched query (%s) found in (%s) - send deal to user %s",
                notification.query,
                search_text,
                notification.user_id,
            )

            return True

        return False
