import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramMigrateToChat,
    TelegramNotFound,
)

from src import config
from src.db.db_utilities import update_user_id
from src.db.user_client import UserClient
from src.models import DealModel, NotificationModel, UserModel
from src.rss.feedparser import FeedParser
from src.telegram.keyboards import Keyboards
from src.telegram.messages import Messages
from src.telegram.routers.admin_router import admin_router
from src.telegram.routers.base_router import base_router
from src.telegram.routers.error_router import error_router
from src.telegram.routers.notification_router import notification_router
from src.telegram.routers.settings_router import settings_router

logger = logging.getLogger(__name__)

properties = DefaultBotProperties(
    parse_mode=ParseMode.HTML,
    link_preview_is_disabled=True,
)


class TelegramBot:
    if not config.BOT_TOKEN:
        msg = "Environment-variable BOT_TOKEN is missing!"
        raise NotImplementedError(msg)

    async def run_bot(self) -> None:
        dp = Dispatcher()

        if config.OWN_ID:
            dp.include_router(admin_router)

        dp.include_routers(base_router, notification_router, settings_router, error_router)

        feedparser = FeedParser(self)
        dp.startup.register(feedparser.start)
        dp.shutdown.register(feedparser.exit)

        await dp.start_polling(Bot(token=config.BOT_TOKEN, default=properties))

    @classmethod
    async def send_deal(cls, deal: DealModel, notification: NotificationModel, user: UserModel) -> None:
        message = Messages.deal_msg(deal, notification)
        keyboard = Keyboards.deal_kb(deal.link, notification)

        bot = Bot(token=config.BOT_TOKEN, default=properties)

        send_message = not user.send_images
        if user.send_images:
            try:
                await bot.send_photo(
                    chat_id=user.id, photo=deal.image_url, caption=message, reply_markup=keyboard, request_timeout=30
                )
            except TelegramAPIError:
                send_message = True

        if send_message:
            try:
                await bot.send_message(chat_id=user.id, text=message, reply_markup=keyboard, request_timeout=30)
            except (TelegramForbiddenError, TelegramNotFound):
                logger.info("User %s blocked the bot. Disable him", notification.user_id)
                UserClient.disable(user.id)
            except TelegramMigrateToChat as e:
                logger.info("Migrate user-id %s to %s", user.id, e.migrate_to_chat_id)
                update_user_id(user, e.migrate_to_chat_id)
            except TelegramBadRequest as e:
                if "chat not found" in e.message.lower():
                    logger.info("Chat %s not found. Disable user.", user.id)
                    UserClient.disable(user.id)
                else:
                    logger.exception("Unexpected exception. User: %s. Message: %s", user.id, message)
            except TelegramAPIError:
                logger.exception("Could not send deal")

        await bot.session.close()
