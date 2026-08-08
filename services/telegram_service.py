import os
import requests

from config import settings
from services.logger import get_logger

logger = get_logger(__name__)

TELEGRAM_SKIPPED = "SKIPPED"
TELEGRAM_SENT = "SENT"
TELEGRAM_FAILED = "FAILED"


def send_message_status(message, confidence_score=None, threshold=80):
    """Send a Telegram message and return SKIPPED, SENT, or FAILED."""
    token = os.getenv("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", settings.TELEGRAM_CHAT_ID)

    if confidence_score is not None and confidence_score < threshold:
        logger.info(
            "Telegram delivery skipped because confidence %.1f is below threshold %.1f",
            confidence_score,
            threshold,
        )
        return TELEGRAM_SKIPPED

    if not token or not chat_id:
        logger.error("Telegram delivery failed: credentials are not configured.")
        return TELEGRAM_FAILED

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": message, "parse_mode": "HTML"},
            timeout=30,
        )
        if response.status_code >= 400:
            logger.error(
                "Telegram send failed with HTTP status %s: %s",
                response.status_code,
                getattr(response, "text", ""),
            )
            return TELEGRAM_FAILED

        logger.info("Telegram message sent successfully")
        return TELEGRAM_SENT
    except requests.RequestException as ex:
        logger.exception("Telegram send failed: %s", ex)
        return TELEGRAM_FAILED


def send_message(message, confidence_score=None, threshold=80):
    """Backward-compatible boolean wrapper around send_message_status."""
    return send_message_status(message, confidence_score, threshold) == TELEGRAM_SENT
