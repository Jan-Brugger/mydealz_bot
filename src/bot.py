import logging

import telegram
from telegram.error import ChatMigrated, TimedOut, Unauthorized
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler, Filters, MessageHandler, \
    PicklePersistence, Updater
from telegram.utils.request import Request

from src.config import Config
from src.core import Core
from src.models import DealModel, NotificationModel
from src.telegram import keyboards, messages
from src.telegram.constants import ADD_NOTIFICATION, DELETE_NOTIFICATION, EDIT_MAX_PRICE, EDIT_NOTIFICATION, EDIT_QUERY, \
    HOME, ONLY_HOT_TOGGLE
from src.telegram.methods import Methods

logger = logging.getLogger(__name__)

QUERY_PATTERN = r'^[\w+&, ]+$'
PRICE_PATTERN = r'^\d+([,\.]\d{1,2})?$'


class Bot:
    def __init__(self) -> None:
        self.__BOT = telegram.Bot(Config.BOT_TOKEN, request=Request(con_pool_size=8))

    def run(self) -> None:
        """Start the bot."""
        persistence = PicklePersistence(filename=Config.CHAT_FILE)
        updater = Updater(bot=self.__BOT, persistence=persistence, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
        add_notification_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(Methods.add_notification_trigger, pattern='^{}$'.format(ADD_NOTIFICATION))
            ],
            states={
                ADD_NOTIFICATION: [MessageHandler(Filters.regex(QUERY_PATTERN), Methods.add_notification)],
            },
            fallbacks=[
                CommandHandler('cancel', Methods.home),
                MessageHandler(Filters.all, Methods.add_notification_failed)
            ],
            allow_reentry=True
        )

        update_query_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(Methods.update_query_trigger, pattern=r'^{}.*$'.format(EDIT_QUERY))
            ],
            states={
                EDIT_QUERY: [MessageHandler(Filters.regex(QUERY_PATTERN), Methods.update_query)],
            },
            fallbacks=[
                CommandHandler('cancel', Methods.show_notification),
                MessageHandler(Filters.all, Methods.update_query_failed)
            ],
            allow_reentry=True
        )

        update_price_conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(Methods.update_price_trigger, pattern=r'^{}.*$'.format(EDIT_MAX_PRICE))
            ],
            states={
                EDIT_MAX_PRICE: [
                    MessageHandler(Filters.regex(PRICE_PATTERN), Methods.update_price),
                    CommandHandler('remove', Methods.update_price)
                ]
            },
            fallbacks=[
                CommandHandler('cancel', Methods.show_notification),
                MessageHandler(Filters.all, Methods.update_price_failed)
            ],
            allow_reentry=True
        )

        dp.add_handler(CommandHandler('start', Methods.start))
        dp.add_handler(CommandHandler('help', Methods.help))
        dp.add_handler(CallbackQueryHandler(Methods.home, pattern=r'^{}$'.format(HOME)))
        dp.add_handler(CallbackQueryHandler(Methods.show_notification, pattern=r'^{}.*$'.format(EDIT_NOTIFICATION)))
        dp.add_handler(CallbackQueryHandler(Methods.toggle_only_hot, pattern=r'^{}.*$'.format(ONLY_HOT_TOGGLE)))
        dp.add_handler(CallbackQueryHandler(Methods.delete_notification, pattern=r'^{}.*$'.format(DELETE_NOTIFICATION)))

        dp.add_handler(add_notification_conversation)
        dp.add_handler(update_query_conversation)
        dp.add_handler(update_price_conversation)

        # log errors
        dp.add_error_handler(Methods.error_handler)

        # start bot
        updater.start_polling()

    def send_deal(self, deal: DealModel, notification: NotificationModel) -> None:
        message = messages.deal_msg(deal, notification)
        keyboard = keyboards.deal_kb(notification)

        try:
            self.__BOT.send_message(
                chat_id=notification.user_id,
                text=message,
                parse_mode=telegram.ParseMode.HTML,
                reply_markup=keyboard
            )
        except (Unauthorized, TimedOut, ChatMigrated) as error:
            logger.error('Some error-handling needed here. %s', error)


def run_bot() -> None:
    Core.init()
    Bot().run()


if __name__ == '__main__':
    run_bot()
