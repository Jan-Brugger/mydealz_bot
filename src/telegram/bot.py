import logging

import telegram
from telegram import Update
from telegram.ext import CallbackContext, Updater, CommandHandler
from telegram.utils.request import Request

from src.config_loader import Config
from src.telegram.methods import Methods

logger = logging.getLogger(__name__)


class Bot:

    def __init__(self) -> None:
        config = Config.get_section('telegram')
        self.__BOT = telegram.Bot(config['token'], request=Request(con_pool_size=8))

    @staticmethod
    def error(update: Update, context: CallbackContext) -> None:
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update.update_id, context.error)

    def run(self) -> None:
        """Start the bot."""
        updater = Updater(bot=self.__BOT, use_context=True)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(CommandHandler('start', Methods.start))
        dp.add_handler(CommandHandler('help', Methods.help))

        # log errors
        dp.add_error_handler(self.error)

        # start bot
        updater.start_polling()

        # gracefully shutdown
        if Config.get_option('general', 'env') != 'dev':
            updater.idle()
