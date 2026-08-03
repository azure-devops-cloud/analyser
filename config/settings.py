"""
Application configuration.
All configuration values should come from here.
"""

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env", override=False)

@dataclass(frozen=True, slots=True)
class Settings:
    """Validated runtime settings loaded from environment variables."""

    base_dir: Path
    app_name: str
    app_version: str
    database_path: Path
    log_file: Path
    telegram_bot_token: str
    telegram_chat_id: str
    debug: bool
    timezone: str

    @classmethod
    def from_environment(cls, base_dir: Path = BASE_DIR) -> "Settings":
        data_dir = base_dir / "data"
        log_dir = base_dir / "logs"
        data_dir.mkdir(exist_ok=True)
        log_dir.mkdir(exist_ok=True)
        return cls(
            base_dir=base_dir,
            app_name="MarketMind AI",
            app_version="0.3.0",
            database_path=data_dir / "marketmind.db",
            log_file=log_dir / "marketmind.log",
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            debug=os.getenv("DEBUG", "false").lower() in {"1", "true", "yes", "on"},
            timezone=os.getenv("TIMEZONE", "Asia/Kolkata"),
        )

    def missing_telegram_credentials(self) -> list[str]:
        missing = []
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.telegram_chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        return missing


SETTINGS = Settings.from_environment()

# Backward-compatible module constants. New code should use SETTINGS.
APP_NAME = SETTINGS.app_name
APP_VERSION = SETTINGS.app_version
DATA_DIR = SETTINGS.database_path.parent
DATABASE_PATH = SETTINGS.database_path
LOG_DIR = SETTINGS.log_file.parent
LOG_FILE = SETTINGS.log_file
TELEGRAM_BOT_TOKEN = SETTINGS.telegram_bot_token
TELEGRAM_CHAT_ID = SETTINGS.telegram_chat_id

# Runtime validation helpers
REQUIRED_ENV_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID"
]

OPTIONAL_ENV_VARS = [
    "DEBUG"
]


def validate_runtime_configuration():
    missing = SETTINGS.missing_telegram_credentials()

    return {
        "required": REQUIRED_ENV_VARS,
        "optional": OPTIONAL_ENV_VARS,
        "missing": missing,
        "debug": SETTINGS.debug
    }


# Runtime
TIMEZONE = SETTINGS.timezone
DEBUG = SETTINGS.debug
