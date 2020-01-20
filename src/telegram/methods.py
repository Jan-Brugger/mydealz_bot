import logging

from telegram import Update
from telegram.ext import CallbackContext

from src.telegram.messages import Messages

logger = logging.getLogger(__name__)


# pylint: disable=unused-argument
class Methods:

    @classmethod
    def start(cls, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            text=Messages.start
        )

    @classmethod
    def help(cls, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            text=Messages.help
        )
