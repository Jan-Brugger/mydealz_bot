import asyncio
import contextlib
import threading
from datetime import datetime

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.config import Config
from src.core import Core
from src.rss.feedparser import FeedParser
from src.telegram.bot import TelegramBot


def parse_job() -> None:
    loop = asyncio.new_event_loop()
    app_scheduler = AsyncIOScheduler(event_loop=loop, timezone=pytz.timezone('Europe/Berlin'))
    app_scheduler.add_job(
        FeedParser().run,
        'interval',
        seconds=Config.PARSE_INTERVAL,
        max_instances=50,
        next_run_time=datetime.now(tz=Config.TIMEZONE),
    )
    app_scheduler.start()

    with contextlib.suppress(KeyboardInterrupt, SystemExit):
        loop.run_forever()


if __name__ == '__main__':
    Core.init()
    threading.Thread(target=parse_job).start()
    TelegramBot().run()
