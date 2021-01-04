from apscheduler.schedulers.background import BackgroundScheduler

from src.bot import Bot
from src.core import Core
from src.feed import Feed

if __name__ == '__main__':
    Core.init()

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(Feed().parse, 'interval', seconds=60)
    scheduler.start()
    Bot().run()
