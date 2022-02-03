import asyncio

from src.core import Core
from src.rss.parser import Parser

if __name__ == '__main__':
    Core.init()
    asyncio.run(Parser().run())
