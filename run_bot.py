from src.core import Core
from src.telegram.bot import TelegramBot

if __name__ == '__main__':
    Core.init()
    telegram_bot = TelegramBot()
    telegram_bot.run()
