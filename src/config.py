from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from pytz import timezone

if TYPE_CHECKING:
    from datetime import tzinfo

load_dotenv()

BOT_TOKEN: str = getenv("BOT_TOKEN", "")
LOG_LEVEL: str = getenv("LOG_LEVEL", "INFO")
FILE_DIR: Path = Path(getenv("FILE_DIR", "./files").rstrip("/"))
LOG_FILE: Path = FILE_DIR / "bot.log"
DATABASE: Path = FILE_DIR / "sqlite_v4.db"
PARSE_INTERVAL: int = int(getenv("PARSE_INTERVAL") or 60)
NOTIFICATION_CAP: int = int(getenv("NOTIFICATION_CAP") or 50)
WHITELIST: list[int] = [int(x.strip()) for x in getenv("WHITELIST", "").split(",") if x.strip()]
BLACKLIST: list[int] = [int(x.strip()) for x in getenv("BLACKLIST", "").split(",") if x.strip()]
TIMEZONE: tzinfo = timezone(getenv("TIMEZONE", "Europe/Berlin"))
OWN_ID: int | None = int(own_id) if (own_id := getenv("OWN_ID")) else None
