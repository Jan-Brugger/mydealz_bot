import logging
from typing import Optional

from telegram import InlineKeyboardMarkup, Update
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
    def error(cls, update: Update, context: CallbackContext) -> None:
        logger.error('Error "%s" caused by update %s', context, update)

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
        context.user_data.clear()
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
        context.user_data.clear()
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
        context.user_data[NOTIFICATION] = notification

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
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )

    @classmethod
    def get_notification(cls, update: Update, context: CallbackContext) -> NotificationModel:
        notification = None
        if NOTIFICATION in context.user_data:
            notification = context.user_data[NOTIFICATION]
        else:
            notification_id = cls.get_callback_variable(update, NOTIFICATION_ID)
            if notification_id:
                notification = SQLiteNotifications().get_by_id(int(notification_id))
                context.user_data[NOTIFICATION] = notification

        if isinstance(notification, NotificationModel):
            return notification

        logging.error('Notification not found in update "%s" with context "%s"', update, context)
        raise FileNotFoundError

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
