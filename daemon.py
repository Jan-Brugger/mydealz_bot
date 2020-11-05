import logging
import time
from threading import Thread

from src.bot import Bot
from src.core import Core
from src.feed import Feed

if __name__ == '__main__':
    Core.init()
    bot = Thread(target=Bot().run)
    bot.daemon = True
    bot.start()

    while True:
        try:
            Feed().parse()
        except Exception as ex:  # pylint: disable=broad-except
            logging.exception(ex)

        time.sleep(60)
