import logging

from src import config
from src.db.db_client import DbClient


class Core:
    @classmethod
    def init(cls) -> None:
        cls._create_files()
        cls._init_logging()
        cls._init_database()

    @classmethod
    def _create_files(cls) -> None:
        if not config.FILE_DIR.is_dir():
            config.FILE_DIR.mkdir(parents=True)

    @classmethod
    def _init_logging(cls) -> None:
        logging.getLogger().setLevel(config.LOG_LEVEL)

        file_log_handler = logging.FileHandler(config.LOG_FILE)
        logging.getLogger().addHandler(file_log_handler)

        stderr_log_handler = logging.StreamHandler()
        logging.getLogger().addHandler(stderr_log_handler)

        log_format = "%(asctime)s - %(levelname)s [%(filename)s:%(lineno)s - %(funcName)s()] %(message)s"
        formatter = logging.Formatter(log_format)
        file_log_handler.setFormatter(formatter)
        stderr_log_handler.setFormatter(formatter)

    @classmethod
    def _init_database(cls) -> None:
        DbClient.init_db()
