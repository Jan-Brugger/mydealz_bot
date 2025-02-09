import asyncio

from src.core import Core
from src.rss.feedparser import FeedParser

if __name__ == "__main__":
    Core.init()
    asyncio.run(FeedParser().run())
