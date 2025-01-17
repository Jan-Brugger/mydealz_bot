import asyncio
import logging
from pathlib import Path

from src.config import Config
from src.db.tables import SQLiteTable


class Core:
    @classmethod
    def init(cls) -> None:
        cls._init_config()
        cls._create_files()
        cls._init_logging()
        asyncio.run(cls._init_database())

    @classmethod
    def _init_config(cls) -> None:
        Config.init()

    @classmethod
    def _create_files(cls) -> None:
        if not Path.is_dir(Config.FILE_DIR):  # type: ignore[arg-type]
            Path.mkdir(Config.FILE_DIR, parents=True)  # type: ignore[arg-type]

    @classmethod
    def _init_logging(cls) -> None:
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
    async def _init_database(cls) -> None:
        tables = SQLiteTable.__subclasses__()
        for table in tables:
            await table().init_table()  # type: ignore[abstract]
