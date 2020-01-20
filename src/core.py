import locale
import logging
import os

from src.config_loader import Config


class Core:
    @classmethod
    def init(cls) -> None:
        locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')
        Config.init(['config/config.ini'])
        cls.__init_logging()

    @staticmethod
    def __init_logging() -> None:
        log_level = Config.get_option('general', 'log_level')
        logging.getLogger().setLevel(log_level)
        log_file = Config.get_option('general', 'log_file')
        path = os.path.dirname(log_file)
        if not os.path.exists(path):
            os.makedirs(path)

        file_log_handler = logging.FileHandler(log_file)
        logging.getLogger().addHandler(file_log_handler)

        stderr_log_handler = logging.StreamHandler()
        logging.getLogger().addHandler(stderr_log_handler)

        # nice output format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_log_handler.setFormatter(formatter)
        stderr_log_handler.setFormatter(formatter)
