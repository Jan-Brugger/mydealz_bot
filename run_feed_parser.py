import asyncio

from src.core import Core
from src.rss.parser import Parser
from src.telegram.bot import TelegramBot

if __name__ == '__main__':
    Core.init()
    bot = TelegramBot()
    asyncio.run(Parser(bot).run())
