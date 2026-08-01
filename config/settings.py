"""
Application configuration.
All configuration values should come from here.
"""

from pathlib import Path
import os

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

if load_dotenv is not None:
    load_dotenv(BASE_DIR / ".env", override=False)

# Application
APP_NAME = "MarketMind AI"
APP_VERSION = "0.2.0"

# Database
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

DATABASE_PATH = DATA_DIR / "marketmind.db"

# Logs
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "marketmind.log"

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Runtime validation helpers
REQUIRED_ENV_VARS = [
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID"
]

OPTIONAL_ENV_VARS = [
    "DEBUG"
]


def validate_runtime_configuration():
    missing = [
        var for var in REQUIRED_ENV_VARS
        if not os.getenv(var, "")
    ]

    return {
        "required": REQUIRED_ENV_VARS,
        "optional": OPTIONAL_ENV_VARS,
        "missing": missing,
        "debug": DEBUG
    }


# Runtime
TIMEZONE = "Asia/Kolkata"
DEBUG = os.getenv("DEBUG", "True").lower() in {"1", "true", "yes", "on"}
