import html
import logging
import traceback
from os import getenv

from telegram import Bot as TelegramBot, ParseMode
from telegram.error import TimedOut, Unauthorized
from telegram.ext import CallbackQueryHandler as CQHandler, CommandHandler as CmdHandler, ConversationHandler, \
    Filters, MessageHandler as MsgHandler, PicklePersistence, Updater
from telegram.utils.request import Request

from src.chat import keyboards, messages
from src.chat.constants import Vars
from src.chat.methods import Methods
from src.config import Config
from src.core import Core
from src.db.tables import SQLiteUser
from src.models import DealModel, NotificationModel

logger = logging.getLogger(__name__)

QUERY_PATTERN = r'^[\w\.+&,\! ]+$'
QUERY_PATTERN_LIMITED_CHARS = r'^[\w\.+&,\! ]{1,59}$'
PRICE_PATTERN = r'^\d+([,\.]\d{1,2})?$'


class Bot:
    def __init__(self) -> None:
        tokens = Config.BOT_TOKENS
        bots = {}
        for token in tokens:
            bot = TelegramBot(token, request=Request(con_pool_size=8))
            bots[bot.id] = bot

        self.__BOTS = bots

    def run(self) -> None:
        """Start the bot."""
        persistence = PicklePersistence(filename=Config.CHAT_FILE)
        updaters = []
        for bot in self.__BOTS.values():
            updaters.append(Updater(bot=bot, persistence=persistence, use_context=True))

        add_notification_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.add_notification_trigger, pattern=fr'^{Vars.ADD_NOTIFICATION}$')
            ],
            states={
                Vars.ADD_NOTIFICATION: [MsgHandler(Filters.regex(QUERY_PATTERN), Methods.add_notification)],
            },
            fallbacks=[
                CmdHandler(Vars.CANCEL, Methods.home),
                MsgHandler(Filters.all, Methods.add_notification_failed)
            ],
            allow_reentry=True
        )

        update_query_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_query_trigger, pattern=fr'^{Vars.EDIT_QUERY}.*$')
            ],
            states={
                Vars.EDIT_QUERY: [MsgHandler(Filters.regex(QUERY_PATTERN), Methods.update_query)],
            },
            fallbacks=[
                CmdHandler(Vars.CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_query_failed)
            ],
            allow_reentry=True
        )

        update_min_price_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_min_price_trigger, pattern=fr'^{Vars.EDIT_MIN_PRICE}.*$')
            ],
            states={
                Vars.EDIT_MIN_PRICE: [
                    MsgHandler(Filters.regex(PRICE_PATTERN), Methods.update_min_price),
                    CmdHandler('remove', Methods.update_min_price)
                ]
            },
            fallbacks=[
                CmdHandler(Vars.CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_min_price_failed)
            ],
            allow_reentry=True
        )

        update_max_price_conversation = ConversationHandler(
            entry_points=[
                CQHandler(Methods.update_max_price_trigger, pattern=fr'^{Vars.EDIT_MAX_PRICE}.*$')
            ],
            states={
                Vars.EDIT_MAX_PRICE: [
                    MsgHandler(Filters.regex(PRICE_PATTERN), Methods.update_max_price),
                    CmdHandler('remove', Methods.update_max_price)
                ]
            },
            fallbacks=[
                CmdHandler(Vars.CANCEL, Methods.show_notification),
                MsgHandler(Filters.all, Methods.update_max_price_failed)
            ],
            allow_reentry=True
        )

        handlers = [
            CmdHandler('start', Methods.start),
            CmdHandler('help', Methods.help),
            CQHandler(Methods.home, pattern=fr'^{Vars.HOME}$'),
            CQHandler(Methods.show_notification, pattern=fr'^{Vars.EDIT_NOTIFICATION}.*$'),
            CQHandler(Methods.toggle_only_hot, pattern=fr'^{Vars.ONLY_HOT_TOGGLE}.*$'),
            CQHandler(Methods.toggle_search_mindstar, pattern=fr'^{Vars.SEARCH_MINDSTAR_TOGGLE}.*$'),
            CQHandler(Methods.delete_notification, pattern=fr'^{Vars.DELETE_NOTIFICATION}.*$'),
            add_notification_conversation,
            update_query_conversation,
            update_min_price_conversation,
            update_max_price_conversation,
            CQHandler(Methods.add_notification, pattern=fr'^{Vars.ADD_NOTIFICATION}.*$'),
            CQHandler(Methods.start, pattern=fr'^{Vars.CANCEL}$'),
            MsgHandler(Filters.regex(QUERY_PATTERN_LIMITED_CHARS), Methods.add_notification_inconclusive)
        ]
        for updater in updaters:

            # add handlers
            for handler in handlers:
                updater.dispatcher.add_handler(handler)  # type: ignore

            # log errors
            updater.dispatcher.add_error_handler(Methods.error_handler)  # type: ignore

            # start bot
            updater.start_polling()

            # gracefully shutdown
            if getenv('ENV') != 'dev':
                updater.idle()

    def send_deal(self, deal: DealModel, notification: NotificationModel, first_try: bool = True) -> None:
        message = messages.deal_msg(deal, notification)
        keyboard = keyboards.deal_kb(notification)
        bot = self.__BOTS.get(notification.bot_id, next(iter(self.__BOTS.values())))

        try:
            bot.send_message(
                chat_id=notification.user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        except Unauthorized:
            logging.info('User %s blocked the bot. Remove all database entries', notification.user_id)
            SQLiteUser().delete_by_id(notification.user_id)

        except TimedOut as error:
            if first_try:
                logging.warning('Sending message timed out, try again.')
                self.send_deal(deal, notification, False)
            else:
                self.send_error(error)

        except Exception as error:  # pylint: disable=broad-except
            self.send_error(error)

    def send_error(self, error: Exception) -> None:
        own_id = getenv('OWN_ID')

        if not own_id:
            return

        tb_string = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )
        bot_id = SQLiteUser().get_bot_id(int(own_id))
        bot = self.__BOTS.get(bot_id, next(iter(self.__BOTS.values())))
        bot.send_message(
            chat_id=own_id,
            text=message,
            parse_mode=ParseMode.HTML,
        )


def run_bot() -> None:
    Core.init()
    Bot().run()


if __name__ == '__main__':
    run_bot()
