from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from src.bot import Bot
from src.core import Core
from src.feed import Feed

if __name__ == '__main__':
    Core.init()

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(Feed().parse, 'interval', seconds=60, timezone=utc)
    scheduler.start()
    Bot().run()
