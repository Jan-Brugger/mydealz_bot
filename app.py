import asyncio
import threading
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src import config
from src.core import Core
from src.rss.feedparser import FeedParser
from src.telegram.bot import TelegramBot


def parse_job() -> None:
    loop = asyncio.new_event_loop()
    app_scheduler = AsyncIOScheduler(event_loop=loop, timezone=config.TIMEZONE)
    app_scheduler.add_job(
        FeedParser().run,
        "interval",
        seconds=config.PARSE_INTERVAL,
        max_instances=50,
        next_run_time=datetime.now(tz=config.TIMEZONE),
    )
    app_scheduler.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        app_scheduler.shutdown()


if __name__ == "__main__":
    Core.init()
    threading.Thread(target=parse_job).start()
    asyncio.run(TelegramBot.run_bot())
