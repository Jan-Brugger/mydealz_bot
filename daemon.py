import time

from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

from src.bot import Bot
from src.core import Core
from src.feed import Feed

if __name__ == '__main__':
    Core.init()

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(
        Feed.parse,
        'interval',
        seconds=60,
        timezone=utc,
        max_instances=50
    )
    scheduler.start()
    Bot().run()

    try:
        # Keep thread alive
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
