"""
Application configuration.
All configuration values should come from here.
"""

from pathlib import Path
import os

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

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

# Runtime
TIMEZONE = "Asia/Kolkata"
DEBUG = True
