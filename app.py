import asyncio
import threading

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.core import Core
from src.rss.parser import Parser
from src.telegram.bot import TelegramBot


def parse_job() -> None:
    loop = asyncio.new_event_loop()
    app_scheduler = AsyncIOScheduler(event_loop=loop, timezone='Europe/Berlin')
    app_scheduler.add_job(
        Parser(TelegramBot()).run,
        'interval',
        seconds=60,
        max_instances=50
    )
    app_scheduler.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    Core.init()
    threading.Thread(target=parse_job).start()
    TelegramBot().run()
