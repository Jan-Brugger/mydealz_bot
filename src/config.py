from os import getenv

from dotenv import load_dotenv


class Config:
    BOT_TOKEN = None
    LOG_LEVEL = 'INFO'
    FILE_DIR = 'files/'
    LOG_FILE = 'bot.log'
    CHAT_FILE = 'chat_data'
    DATABASE = 'sqlite.db'
    LAST_UPDATE_ALL = 'last_update_all.txt'
    LAST_UPDATE_HOT = 'last_update_hot.txt'

    @classmethod
    def init(cls) -> None:
        load_dotenv()

        if not getenv('BOT_TOKEN'):
            raise NotImplementedError('Environment-variable BOT_TOKEN is missing!')
        cls.BOT_TOKEN = getenv('BOT_TOKEN')
        cls.LOG_LEVEL = getenv('LOG_LEVEL') or cls.LOG_LEVEL
        cls.FILE_DIR = (getenv('FILE_DIR') or cls.FILE_DIR).rstrip('/')
        cls.LOG_FILE = '{}/{}'.format(cls.FILE_DIR, getenv('LOG_FILE') or cls.LOG_FILE)
        cls.CHAT_FILE = '{}/{}'.format(cls.FILE_DIR, getenv('CHAT_FILE') or cls.CHAT_FILE)
        cls.DATABASE = '{}/{}'.format(cls.FILE_DIR, getenv('DATABASE') or cls.DATABASE)
        cls.LAST_UPDATE_ALL = '{}/{}'.format(cls.FILE_DIR, getenv('LAST_UPDATE_ALL') or cls.LAST_UPDATE_ALL)
        cls.LAST_UPDATE_HOT = '{}/{}'.format(cls.FILE_DIR, getenv('LAST_UPDATE_HOT') or cls.LAST_UPDATE_HOT)
