from aiogram import types
from aiogram.dispatcher.filters import Filter

from src.config import Config


class NotWhitelistedFilter(Filter):
    key = 'whitelist'

    @classmethod
    async def check(cls, message: types.Message) -> bool:
        return message.chat.id not in Config.WHITELIST if Config.WHITELIST else False


class BlacklistedFilter(Filter):
    key = 'blacklist'

    @classmethod
    async def check(cls, message: types.Message) -> bool:
        return message.chat.id in Config.BLACKLIST or message.from_user.id in Config.BLACKLIST
