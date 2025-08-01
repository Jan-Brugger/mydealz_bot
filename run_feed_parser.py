import asyncio

from src.core import Core
from src.rss.feedparser import FeedParser
from src.telegram.bot import TelegramBot

if __name__ == "__main__":
    Core.init()
    asyncio.run(FeedParser(TelegramBot()).parse_feeds())
