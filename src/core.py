import logging
import os
from os.path import isdir, isfile

from src.config import Config
from src.db.tables import SQLiteTable


class Core:
    @classmethod
    def init(cls) -> None:
        # locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8') # TODO Fix locale for docker  # pylint: disable=fixme
        cls.__init_config()
        cls.__create_files()
        cls.__init_logging()
        cls.__init_database()

    @classmethod
    def __init_config(cls) -> None:
        Config.init()

    @classmethod
    def __create_files(cls) -> None:
        if not isdir(Config.FILE_DIR):
            os.makedirs(Config.FILE_DIR)

        if not isfile(Config.LAST_UPDATE_ALL):
            f = open(Config.LAST_UPDATE_ALL, 'w')
            f.close()

        if not isfile(Config.LAST_UPDATE_HOT):
            f = open(Config.LAST_UPDATE_HOT, 'w')
            f.close()

    @classmethod
    def __init_logging(cls) -> None:
        logging.getLogger().setLevel(Config.LOG_LEVEL)

        file_log_handler = logging.FileHandler(Config.LOG_FILE)
        logging.getLogger().addHandler(file_log_handler)

        stderr_log_handler = logging.StreamHandler()
        logging.getLogger().addHandler(stderr_log_handler)

        log_format = '%(asctime)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s'
        formatter = logging.Formatter(log_format)
        file_log_handler.setFormatter(formatter)
        stderr_log_handler.setFormatter(formatter)

    @classmethod
    def __init_database(cls) -> None:
        tables = SQLiteTable.__subclasses__()
        for table in tables:
            table().init_table()  # type: ignore
