from os import getenv
from typing import ClassVar

import pytz
from dotenv import load_dotenv


class Config:
    BOT_TOKEN = ''
    LOG_LEVEL = 'INFO'
    FILE_DIR = 'files/'
    LOG_FILE = 'bot.log'
    CHAT_FILE = 'chat_data'
    DATABASE = 'sqlite_v2.db'
    TIMEZONE = pytz.timezone('Europe/Berlin')
    PARSE_INTERVAL = 60
    NOTIFICATION_CAP = 50
    WHITELIST: ClassVar[list[int]] = []
    BLACKLIST: ClassVar[list[int]] = []

    @classmethod
    def init(cls) -> None:
        load_dotenv()

        token = getenv('BOT_TOKEN')
        if not token:
            msg = 'Environment-variable BOT_TOKEN is missing!'
            raise NotImplementedError(msg)

        cls.BOT_TOKEN = token
        cls.LOG_LEVEL = getenv('LOG_LEVEL') or cls.LOG_LEVEL
        cls.FILE_DIR = (getenv('FILE_DIR') or cls.FILE_DIR).rstrip('/')
        cls.LOG_FILE = f'{cls.FILE_DIR}/{getenv("LOG_FILE") or cls.LOG_FILE}'
        cls.CHAT_FILE = f'{cls.FILE_DIR}/{getenv("CHAT_FILE") or cls.CHAT_FILE}'
        cls.DATABASE = f'{cls.FILE_DIR}/{getenv("DATABASE") or cls.DATABASE}'
        interval = getenv('PARSE_INTERVAL')
        cls.PARSE_INTERVAL = int(interval) if interval else cls.PARSE_INTERVAL
        cls.NOTIFICATION_CAP = int(getenv('NOTIFICATION_CAP') or cls.NOTIFICATION_CAP)
        cls.WHITELIST = [int(x.strip()) for x in getenv('WHITELIST', '').split(',') if x.strip()]
        cls.BLACKLIST = [int(x.strip()) for x in getenv('BLACKLIST', '').split(',') if x.strip()]
