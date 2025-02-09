import asyncio
import logging
from datetime import datetime, timedelta
from threading import Event, Thread

from src import config
from src.core import Core
from src.rss.feedparser import FeedParser
from src.telegram.bot import TelegramBot

logger = logging.getLogger(__name__)

exit_event = Event()


class ParseJob(Thread):
    run_job = True

    def run(self) -> None:  # noqa: PLR6301
        try:
            while not exit_event.is_set():
                try:
                    asyncio.run(FeedParser.run())
                except Exception:
                    logger.exception("Error while parsing / sending deals")

                logger.info(
                    "Next feedparser-run: %s",
                    datetime.now(tz=config.TIMEZONE) + timedelta(seconds=config.PARSE_INTERVAL),
                )
                exit_event.wait(config.PARSE_INTERVAL)
        except (KeyboardInterrupt, SystemExit):
            pass


if __name__ == "__main__":
    Core.init()
    thread = ParseJob()
    thread.start()

    asyncio.run(TelegramBot.run_bot())
    exit_event.set()
