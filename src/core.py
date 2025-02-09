import logging
import sqlite3

from src import config
from src.config import DATABASE, FILE_DIR
from src.db.db_client import DbClient
from src.db.notification_client import NotificationClient
from src.db.user_client import UserClient
from src.models import NotificationModel, UserModel


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
        migrate_db = (FILE_DIR / "sqlite_v2.db").is_file() and not DATABASE.is_file()
        DbClient.init_db()

        if migrate_db:
            cls.migrate_db()

    @classmethod
    def migrate_db(cls) -> None:
        con = sqlite3.connect(FILE_DIR / "sqlite_v2.db")
        cur = con.cursor()

        for user in cur.execute(
            "SELECT u_id, username, first_name, last_name, search_md, search_pj, active, send_images FROM users"
        ):
            user_model = UserModel(
                id=int(user[0]),
                username=str(user[1]),
                first_name=str(user[2]),
                last_name=str(user[3]),
                search_mydealz=bool(user[4]),
                search_preisjaeger=bool(user[5]),
                active=bool(user[6]),
                send_images=bool(user[7]),
            )

            UserClient.add(user_model)

        for notification in cur.execute(
            "SELECT n_id, query, min_price, max_price, hot_only, search_descr, user_id FROM notifications"
        ):
            notification_model = NotificationModel(
                id=int(notification[0]),
                query=str(notification[1]),
                min_price=int(notification[2]),
                max_price=int(notification[3]),
                search_hot_only=bool(notification[4]),
                search_description=bool(notification[5]),
                user_id=int(notification[6]),
            )

            NotificationClient.add(notification_model)
