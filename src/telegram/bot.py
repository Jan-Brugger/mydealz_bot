import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError, TelegramForbiddenError, TelegramMigrateToChat

from src import config
from src.db.db_client import DbClient
from src.db.user_client import UserClient
from src.models import DealModel, NotificationModel, UserModel
from src.telegram.keyboards import Keyboards
from src.telegram.messages import Messages
from src.telegram.routers.admin_router import admin_router
from src.telegram.routers.base_router import base_router
from src.telegram.routers.error_router import error_router
from src.telegram.routers.notification_router import notification_router
from src.telegram.routers.settings_router import settings_router

logger = logging.getLogger(__name__)


class TelegramBot:
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview_is_disabled=True,
        ),
    )

    @classmethod
    async def run_bot(cls) -> None:
        dp = Dispatcher()

        if config.OWN_ID:
            dp.include_router(admin_router)

        dp.include_routers(base_router, notification_router, settings_router, error_router)

        await dp.start_polling(cls.bot)

    @classmethod
    async def send_deal(cls, deal: DealModel, notification: NotificationModel, user: UserModel) -> None:
        message = Messages.deal_msg(deal, notification)
        keyboard = Keyboards.deal_kb(deal.link, notification)

        if user.send_images:
            try:
                await cls.bot.send_photo(
                    chat_id=user.id,
                    photo=deal.image_url,
                    caption=message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                )
            except TelegramAPIError:
                pass
            else:
                return

        try:
            await cls.bot.send_message(chat_id=user.id, text=message, parse_mode=ParseMode.HTML, reply_markup=keyboard)
        except TelegramForbiddenError:
            logger.info("User %s blocked the bot. Disable him", notification.user_id)
            UserClient.disable(user.id)
        except TelegramMigrateToChat as e:
            logger.info("Migrate user-id %s to %s", user.id, e.migrate_to_chat_id)
            user = DbClient.update_user_id(user, e.migrate_to_chat_id)

            await cls.send_deal(deal, notification, user)
        except TelegramAPIError:
            logger.exception("Could not send deal")
