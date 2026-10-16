"""Centralized runtime configuration for MarketMind."""

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
    model_provider: str
    model_name: str
    model_temperature: float
    model_max_tokens: int
    model_timeout: float
    agent_max_retries: int
    agent_backoff_seconds: float
    agent_stop_on_critical_failure: bool
    telemetry_enabled: bool

    @classmethod
    def from_environment(cls, base_dir: Path = BASE_DIR) -> "Settings":
        data_dir = base_dir / "data"
        log_dir = base_dir / "logs"
        data_dir.mkdir(exist_ok=True)
        log_dir.mkdir(exist_ok=True)

        def as_float(name: str, default: float) -> float:
            try:
                return float(os.getenv(name, str(default)))
            except ValueError:
                return default

        def as_int(name: str, default: int) -> int:
            try:
                return int(os.getenv(name, str(default)))
            except ValueError:
                return default

        as_bool = lambda name, default=False: os.getenv(name, str(default)).lower() in {"1", "true", "yes", "on"}

        return cls(
            base_dir=base_dir,
            app_name="MarketMind AI",
            app_version="0.4.0",
            database_path=data_dir / "marketmind.db",
            log_file=log_dir / "marketmind.log",
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
            debug=as_bool("DEBUG"),
            timezone=os.getenv("TIMEZONE", "Asia/Kolkata"),
            model_provider=os.getenv("MODEL_PROVIDER", "ollama"),
            model_name=os.getenv("MODEL_NAME", "qwen3:4b"),
            model_temperature=as_float("MODEL_TEMPERATURE", 0.0),
            model_max_tokens=as_int("MODEL_MAX_TOKENS", 2048),
            model_timeout=as_float("MODEL_TIMEOUT", 30.0),
            agent_max_retries=as_int("AGENT_MAX_RETRIES", 1),
            agent_backoff_seconds=as_float("AGENT_BACKOFF_SECONDS", 0.25),
            agent_stop_on_critical_failure=as_bool("AGENT_STOP_ON_CRITICAL_FAILURE"),
            telemetry_enabled=as_bool("TELEMETRY_ENABLED"),
        )

    def missing_telegram_credentials(self) -> list[str]:
        missing = []
        if not self.telegram_bot_token:
            missing.append("TELEGRAM_BOT_TOKEN")
        if not self.telegram_chat_id:
            missing.append("TELEGRAM_CHAT_ID")
        return missing


SETTINGS = Settings.from_environment()

# Backward-compatible module constants.
APP_NAME = SETTINGS.app_name
APP_VERSION = SETTINGS.app_version
DATA_DIR = SETTINGS.database_path.parent
DATABASE_PATH = SETTINGS.database_path
LOG_DIR = SETTINGS.log_file.parent
LOG_FILE = SETTINGS.log_file
TELEGRAM_BOT_TOKEN = SETTINGS.telegram_bot_token
TELEGRAM_CHAT_ID = SETTINGS.telegram_chat_id
TIMEZONE = SETTINGS.timezone
DEBUG = SETTINGS.debug
MODEL_PROVIDER = SETTINGS.model_provider
MODEL_NAME = SETTINGS.model_name
MODEL_TEMPERATURE = SETTINGS.model_temperature
MODEL_MAX_TOKENS = SETTINGS.model_max_tokens
MODEL_TIMEOUT = SETTINGS.model_timeout
AGENT_MAX_RETRIES = SETTINGS.agent_max_retries
AGENT_BACKOFF_SECONDS = SETTINGS.agent_backoff_seconds
AGENT_STOP_ON_CRITICAL_FAILURE = SETTINGS.agent_stop_on_critical_failure
TELEMETRY_ENABLED = SETTINGS.telemetry_enabled

REQUIRED_ENV_VARS = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
OPTIONAL_ENV_VARS = [
    "DEBUG",
    "TIMEZONE",
    "MODEL_PROVIDER",
    "MODEL_NAME",
    "MODEL_TEMPERATURE",
    "MODEL_MAX_TOKENS",
    "MODEL_TIMEOUT",
    "AGENT_MAX_RETRIES",
    "AGENT_BACKOFF_SECONDS",
    "AGENT_STOP_ON_CRITICAL_FAILURE",
    "TELEMETRY_ENABLED",
]


def validate_runtime_configuration():
    """Return non-secret configuration health information."""
    return {
        "required": REQUIRED_ENV_VARS,
        "optional": OPTIONAL_ENV_VARS,
        "missing": SETTINGS.missing_telegram_credentials(),
        "debug": SETTINGS.debug,
        "model": {
            "provider": SETTINGS.model_provider,
            "model": SETTINGS.model_name,
            "temperature": SETTINGS.model_temperature,
            "max_tokens": SETTINGS.model_max_tokens,
            "timeout": SETTINGS.model_timeout,
        },
        "agent_runtime": {
            "max_retries": SETTINGS.agent_max_retries,
            "backoff_seconds": SETTINGS.agent_backoff_seconds,
            "stop_on_critical_failure": SETTINGS.agent_stop_on_critical_failure,
        },
        "telemetry_enabled": SETTINGS.telemetry_enabled,
    }
