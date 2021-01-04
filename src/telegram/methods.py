import html
import json
import logging
import traceback
from os import getenv
from typing import Any, Optional

from telegram import InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler

from src.db import columns
from src.db.tables import SQLiteNotifications, SQLiteUser
from src.models import NotificationModel, UserModel
from src.telegram import keyboards, messages
from src.telegram.constants import ADD_NOTIFICATION, EDIT_MAX_PRICE, EDIT_QUERY, NOTIFICATION, NOTIFICATION_ID

logger = logging.getLogger(__name__)

END_CONVERSATION: int = ConversationHandler.END


# pylint: disable=unused-argument
class Methods:

    @classmethod
    def error_handler(cls, update: Update, context: CallbackContext) -> None:
        if not context.error:
            logger.error('Exception while handling following update: %s', update)

            return

        logger.error(msg='Exception while handling an update:', exc_info=context.error)
        own_id = getenv('OWN_ID')

        if not own_id:
            return

        tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
        tb_string = ''.join(tb_list)

        message = (
            f'An exception was raised while handling an update\n'
            f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
            '</pre>\n\n'
            f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
            f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
            f'<pre>{html.escape(tb_string)}</pre>'
        )

        context.bot.send_message(chat_id=own_id, text=message, parse_mode=ParseMode.HTML)

    @classmethod
    def start(cls, update: Update, context: CallbackContext) -> int:
        logging.debug('%s %s', update, context)
        sqlite_user = SQLiteUser()
        user = sqlite_user.get_by_id(cls.get_user_id(update))
        new_user = UserModel().parse_telegram_user(update)
        if not user or user != new_user:
            logging.info('added user: %s', new_user.__dict__)
            sqlite_user.upsert_model(new_user)

        notifications = SQLiteNotifications().get_by_user_id(cls.get_user_id(update))
        cls.send_message(update, context, messages.start(), keyboards.start(notifications))

        # cleanup
        cls.clear_user_data(context)
        return END_CONVERSATION

    @classmethod
    def help(cls, update: Update, context: CallbackContext) -> int:
        cls.send_message(update, context, messages.help_msg(), parse_mode='HTML')

        return END_CONVERSATION

    @classmethod
    def home(cls, update: Update, context: CallbackContext, add_message: str = '') -> int:
        logging.debug('%s %s', update, context)
        notifications = SQLiteNotifications().get_by_user_id(cls.get_user_id(update))

        message = '{}\n\n{}'.format(add_message, messages.start()) if add_message else messages.start()
        cls.overwrite_message(update, context, message, keyboards.start(notifications))

        # cleanup
        cls.clear_user_data(context)
        return END_CONVERSATION

    @classmethod
    def add_notification_trigger(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.overwrite_message(update, context, messages.query_instructions())

        return ADD_NOTIFICATION

    @classmethod
    def add_notification(cls, update: Update, context: CallbackContext) -> int:
        logging.debug('%s %s', update, context)
        notification = NotificationModel()
        notification.user_id = cls.get_user_id(update)
        notification.query = cls.get_text(update)
        notification.id = SQLiteNotifications().upsert_model(notification)
        cls.set_user_data(context, NOTIFICATION, notification)

        logging.info('user %s added notification %s (%s)', notification.user_id, notification.id, notification.query)
        cls.send_message(update, context, messages.notification_added(notification),
                         keyboards.notification_commands(notification))

        return END_CONVERSATION

    @classmethod
    def add_notification_failed(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.send_message(update, context, messages.invalid_query())

        return ADD_NOTIFICATION

    @classmethod
    def show_notification(cls, update: Update, context: CallbackContext, overwrite: bool = False) -> int:
        logging.debug('%s %s', update, context)
        notification = cls.get_notification(update, context)

        if overwrite:
            cls.overwrite_message(update, context, messages.notification_overview(notification),
                                  keyboards.notification_commands(notification))
        else:
            cls.send_message(update, context, messages.notification_overview(notification),
                             keyboards.notification_commands(notification))

        return END_CONVERSATION

    @classmethod
    def update_query_trigger(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.send_message(update, context, messages.query_instructions())

        return EDIT_QUERY

    @classmethod
    def update_query(cls, update: Update, context: CallbackContext) -> int:
        logging.debug('%s %s', update, context)
        notification = cls.get_notification(update, context)
        notification.query = cls.get_text(update)
        SQLiteNotifications().update(notification.id, columns.QUERY, notification.query)

        cls.send_message(update, context, messages.query_updated(notification),
                         keyboards.notification_commands(notification))

        return END_CONVERSATION

    @classmethod
    def update_query_failed(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.send_message(update, context, messages.invalid_query())

        return EDIT_QUERY

    @classmethod
    def update_price_trigger(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.send_message(update, context, messages.price_instructions())

        return EDIT_MAX_PRICE

    @classmethod
    def update_price(cls, update: Update, context: CallbackContext) -> int:
        logging.debug('%s %s', update, context)
        price = cls.get_text(update)
        if price == '/remove':
            price = '0'

        notification = cls.get_notification(update, context)
        notification.max_price = round(float(price.replace(',', '.')))
        SQLiteNotifications().update(notification.id, columns.MAX_PRICE, notification.max_price)

        cls.send_message(update, context, messages.query_updated(notification),
                         keyboards.notification_commands(notification))

        return END_CONVERSATION

    @classmethod
    def update_price_failed(cls, update: Update, context: CallbackContext) -> str:
        logging.debug('%s %s', update, context)
        cls.send_message(update, context, messages.invalid_price())

        return EDIT_MAX_PRICE

    @classmethod
    def toggle_only_hot(cls, update: Update, context: CallbackContext) -> None:
        logging.debug('%s %s', update, context)
        notification = cls.get_notification(update, context)
        notification.search_only_hot = not notification.search_only_hot
        SQLiteNotifications().update(notification.id, columns.ONLY_HOT, notification.search_only_hot)

        cls.show_notification(update, context, True)

    @classmethod
    def delete_notification(cls, update: Update, context: CallbackContext) -> None:
        logging.debug('%s %s', update, context)
        notification = cls.get_notification(update, context)
        SQLiteNotifications().delete_by_id(notification.id)

        logging.info('user %s deleted notification %s (%s)', notification.user_id, notification.id, notification.query)
        cls.home(update, context, messages.notification_deleted(notification))

    @classmethod
    def get_user_id(cls, update: Update) -> int:
        if not update.effective_user:
            raise Exception('User is missing for update', update)

        return int(update.effective_user.id)

    @classmethod
    def get_text(cls, update: Update) -> str:
        return str(update.message.text)

    @classmethod
    def overwrite_message(cls, update: Update, context: CallbackContext,
                          text: str,
                          reply_markup: Optional[InlineKeyboardMarkup] = None,
                          parse_mode: Optional[str] = None) -> None:
        try:
            update.callback_query.edit_message_text(text)
            if reply_markup:
                update.callback_query.edit_message_reply_markup(reply_markup)
        except AttributeError:
            logging.debug('replace failed, send new message instead. %s %s', update, context)
            cls.send_message(update, context, text, reply_markup, parse_mode)

    @classmethod
    def send_message(cls, update: Update, context: CallbackContext,
                     text: str,
                     reply_markup: Optional[InlineKeyboardMarkup] = None,
                     parse_mode: Optional[str] = None) -> None:
        # remove old keyboard
        try:
            context.bot.edit_message_reply_markup(
                cls.get_user_id(update),
                update.callback_query.message.message_id
            )
        except AttributeError:
            pass

        context.bot.send_message(
            chat_id=cls.get_user_id(update),
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

    @classmethod
    def get_notification(cls, update: Update, context: CallbackContext) -> NotificationModel:
        notification = cls.get_user_data(context, NOTIFICATION)
        if not notification:
            notification_id = cls.get_callback_variable(update, NOTIFICATION_ID)
            if notification_id:
                notification = SQLiteNotifications().get_by_id(int(notification_id))
                cls.set_user_data(context, NOTIFICATION, notification)

        if not isinstance(notification, NotificationModel):
            raise Exception('Notification not found!')

        return notification

    @classmethod
    def get_callback_variable(cls, update: Update, variable: str) -> Optional[str]:
        variable_pattern = '!!{}='.format(variable)
        if not update.callback_query or not update.callback_query.data:
            return ''

        cb_data = str(update.callback_query.data)
        start = cb_data.find(variable_pattern)

        if start == -1:
            logger.warning('Variable %s not found in %s', variable, update)

            return None

        start += len(variable_pattern)
        end = cb_data.find('!', start) if cb_data.find('!', start) != -1 else len(cb_data)

        return cb_data[start: end]

    @classmethod
    def get_user_data(cls, context: CallbackContext, key: str) -> Any:
        return context.user_data.get(key) if context.user_data else None

    @classmethod
    def set_user_data(cls, context: CallbackContext, key: str, value: Any) -> None:
        if not isinstance(context.user_data, dict):
            raise Exception('user_data is not a dictionary')

        context.user_data[key] = value

    @classmethod
    def clear_user_data(cls, context: CallbackContext) -> None:
        if context.user_data:
            context.user_data.clear()
