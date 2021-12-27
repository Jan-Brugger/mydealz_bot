import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

from src.bot import Bot
from src.core import Core
from src.parser import Parser

if __name__ == '__main__':
    Core.init()

    scheduler = AsyncIOScheduler()
    job = scheduler.add_job(
        Parser.parse,
        'interval',
        seconds=60,
        timezone=utc,
        max_instances=50
    )
    scheduler.start()
    Bot().run()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
