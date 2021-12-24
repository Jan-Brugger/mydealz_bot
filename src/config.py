from os import getenv
from typing import List

from dotenv import load_dotenv


class Config:
    BOT_TOKENS: List[str] = []
    LOG_LEVEL = 'INFO'
    FILE_DIR = 'files/'
    LOG_FILE = 'bot.log'
    CHAT_FILE = 'chat_data'
    DATABASE = 'sqlite_v2.db'

    @classmethod
    def init(cls) -> None:
        load_dotenv()

        tokens = getenv('BOT_TOKEN', '').replace(' ', '').split(',')
        if not tokens:
            raise NotImplementedError('Environment-variable BOT_TOKEN is missing!')

        cls.BOT_TOKENS = tokens
        cls.LOG_LEVEL = getenv('LOG_LEVEL') or cls.LOG_LEVEL
        cls.FILE_DIR = (getenv('FILE_DIR') or cls.FILE_DIR).rstrip('/')
        cls.LOG_FILE = f'{cls.FILE_DIR}/{getenv("LOG_FILE") or cls.LOG_FILE}'
        cls.CHAT_FILE = f'{cls.FILE_DIR}/{getenv("CHAT_FILE") or cls.CHAT_FILE}'
        cls.DATABASE = f'{cls.FILE_DIR}/{getenv("DATABASE") or cls.DATABASE}'
