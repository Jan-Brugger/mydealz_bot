import logging
import sqlite3

from src import config
from src.config import DATABASE, FILE_DIR
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
        db_exists = DATABASE.is_file()
        DbClient.init_db()
        if not db_exists:
            if (FILE_DIR / "sqlite_v3.db").is_file():
                cls.migrate_from_v3()
            elif (FILE_DIR / "sqlite_v2.db").is_file():
                cls.migrate_from_v2()

    @classmethod
    def migrate_from_v2(cls) -> None:
        with sqlite3.connect(config.DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"ATTACH DATABASE '{FILE_DIR / 'sqlite_v2.db'}' AS old;")
            cur.execute(
                "INSERT INTO users(id, username, first_name, last_name, search_mydealz, search_preisjaeger, send_images, active) "  # noqa: E501
                "SELECT u_id, username, first_name, last_name, search_md, search_pj, send_images, active FROM old.users;"  # noqa: E501
            )
            cur.execute(
                "INSERT INTO notifications(id, search_query, min_price, max_price, search_hot_only, search_description, user_id) "  # noqa: E501
                "SELECT n_id, query, min_price, max_price, hot_only, search_descr, user_id FROM old.notifications;"
            )
            con.commit()

    @classmethod
    def migrate_from_v3(cls) -> None:
        with sqlite3.connect(config.DATABASE) as con:
            cur = con.cursor()
            cur.execute(f"ATTACH DATABASE '{FILE_DIR / 'sqlite_v3.db'}' AS old;")
            cur.execute("INSERT INTO users SELECT * FROM old.users;")
            cur.execute(
                "INSERT INTO notifications(id, search_query, min_price, max_price, search_hot_only, search_description, user_id) "  # noqa: E501
                "SELECT id, query, min_price, max_price, search_hot_only, search_description, user_id FROM old.notifications;"  # noqa: E501
            )
            con.commit()
