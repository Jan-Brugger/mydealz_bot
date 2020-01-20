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
        Feed().parse()
        time.sleep(60)
