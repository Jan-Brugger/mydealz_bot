from aiogram import types
from aiogram.dispatcher.filters import Filter

from src.config import Config


class NotWhitelistedFilter(Filter):
    key = 'whitelist'

    async def check(self, message: types.Message) -> bool:  # pylint: disable=arguments-differ
        return message.chat.id not in Config.WHITELIST if Config.WHITELIST else False


class BlacklistedFilter(Filter):
    key = 'blacklist'

    async def check(self, message: types.Message) -> bool:  # pylint: disable=arguments-differ
        return message.chat.id in Config.BLACKLIST or message.from_user.id in Config.BLACKLIST
