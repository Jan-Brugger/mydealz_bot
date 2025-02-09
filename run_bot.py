import asyncio

from src.core import Core
from src.telegram.bot import TelegramBot

if __name__ == "__main__":
    Core.init()
    asyncio.run(TelegramBot.run_bot())
