import logging
from os import getenv

from telegram import Bot as TelegramBot, ParseMode
from telegram.error import ChatMigrated, TimedOut, Unauthorized
from telegram.ext import CallbackQueryHandler as CQHandler, CommandHandler as CmdHandler, \
    ConversationHandler, \
    Filters, MessageHandler as MsgHandler, PicklePersistence, Updater
from telegram.utils.request import Request

from src.config import Config
from src.core import Core
from src.models import DealModel, NotificationModel
from src.telegram import keyboards, messages
from src.telegram.constants import ADD_NOTIFICATION, CANCEL, DELETE_NOTIFICATION, EDIT_MAX_PRICE, EDIT_MIN_PRICE, \
    EDIT_NOTIFICATION, EDIT_QUERY, HOME, ONLY_HOT_TOGGLE
from src.telegram.methods import Methods

logger = logging.getLogger(__name__)

QUERY_PATTERN = r'^[\w+&, ]+$'
PRICE_PATTERN = r'^\d+([,\.]\d{1,2})?$'


class Bot:
    def __init__(self) -> None:
        self.__BOT = TelegramBot(Config.BOT_TOKEN, request=Request(con_pool_size=8))

    def run(self) -> None:
        """Start the bot."""
        persistence = PicklePersistence(filename=Config.CHAT_FILE)
        updater = Updater(bot=self.__BOT, persistence=persistence, use_context=True)

        add_notification_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.add_notification_trigger, pattern='^{}$'.format(ADD_NOTIFICATION))
            ],
            states={
                ADD_NOTIFICATION: [MsgHandler(Filters.regex(QUERY_PATTERN), Methods.add_notification)],
            },
            fallbacks=[
                CmdHandler(CANCEL, Methods.home),
                MsgHandler(Filters.all, Methods.add_notification_failed)
            ],
            allow_reentry=True
        )

        update_query_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_query_trigger, pattern=r'^{}.*$'.format(EDIT_QUERY))
            ],
            states={
                EDIT_QUERY: [MsgHandler(Filters.regex(QUERY_PATTERN), Methods.update_query)],
            },
            fallbacks=[
                CmdHandler(CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_query_failed)
            ],
            allow_reentry=True
        )

        update_min_price_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_min_price_trigger, pattern=r'^{}.*$'.format(EDIT_MIN_PRICE))
            ],
            states={
                EDIT_MIN_PRICE: [
                    MsgHandler(Filters.regex(PRICE_PATTERN), Methods.update_min_price),
                    CmdHandler('remove', Methods.update_min_price)
                ]
            },
            fallbacks=[
                CmdHandler(CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_min_price_failed)
            ],
            allow_reentry=True
        )

        update_max_price_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_max_price_trigger, pattern=r'^{}.*$'.format(EDIT_MAX_PRICE))
            ],
            states={
                EDIT_MAX_PRICE: [
                    MsgHandler(Filters.regex(PRICE_PATTERN), Methods.update_max_price),
                    CmdHandler('remove', Methods.update_max_price)
                ]
            },
            fallbacks=[
                CmdHandler(CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_max_price_failed)
            ],
            allow_reentry=True
        )

        handlers = [
            CmdHandler('start', Methods.start),
            CmdHandler('help', Methods.help),
            CQHandler(Methods.home, pattern=r'^{}$'.format(HOME)),
            CQHandler(Methods.show_notification, pattern=r'^{}.*$'.format(EDIT_NOTIFICATION)),
            CQHandler(Methods.toggle_only_hot, pattern=r'^{}.*$'.format(ONLY_HOT_TOGGLE)),
            CQHandler(Methods.delete_notification, pattern=r'^{}.*$'.format(DELETE_NOTIFICATION)),
            add_notification_conversation,
            update_query_conversation,
            update_min_price_conversation,
            update_max_price_conversation,
            CQHandler(Methods.add_notification, pattern=r'^{}.*$'.format(ADD_NOTIFICATION)),
            CQHandler(Methods.start, pattern=r'^{}$'.format(CANCEL)),
            MsgHandler(Filters.regex(QUERY_PATTERN), Methods.add_notification_inconclusive)
        ]

        dispatcher = updater.dispatcher  # type:ignore

        # add handlers
        for handler in handlers:
            dispatcher.add_handler(handler)

        # log errors
        dispatcher.add_error_handler(Methods.error_handler)

        # start bot
        updater.start_polling()

        # gracefully shutdown
        if getenv('ENV') != 'dev':
            updater.idle()

    def send_deal(self, deal: DealModel, notification: NotificationModel) -> None:
        message = messages.deal_msg(deal, notification)
        keyboard = keyboards.deal_kb(notification)

        try:
            self.__BOT.send_message(
                chat_id=notification.user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        except (Unauthorized, TimedOut, ChatMigrated) as error:
            logger.error('Some error-handling needed here. %s', error)


def run_bot() -> None:
    Core.init()
    Bot().run()


if __name__ == '__main__':
    run_bot()
