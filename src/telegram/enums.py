from enum import StrEnum


class BotCommand(StrEnum):
    CANCEL = "cancel"
    REMOVE = "remove"
    HELP = "help"
    SETTINGS = "settings"
    BROADCAST = "broadcast"
