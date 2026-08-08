import os
import requests

from config import settings
from services.logger import get_logger

logger = get_logger(__name__)


def send_message(message, confidence_score=None, threshold=80):

    token = os.getenv(
        "TELEGRAM_BOT_TOKEN",
        settings.TELEGRAM_BOT_TOKEN
    )

    chat_id = os.getenv(
        "TELEGRAM_CHAT_ID",
        settings.TELEGRAM_CHAT_ID
    )

    if confidence_score is not None and confidence_score < threshold:
        logger.info(
            "Telegram delivery skipped because confidence %.1f is below threshold %.1f",
            confidence_score,
            threshold,
        )
        return False

    if not token or not chat_id:
        logger.warning(
            "Telegram credentials are not configured. Skipping Telegram notification."
        )
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        response = requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            },
            timeout=30
        )

        # Keep this compatible with real requests.Response objects and
        # lightweight response doubles used by the test suite.
        if response.status_code >= 400:
            logger.error(
                "Telegram send failed with HTTP status %s: %s",
                response.status_code,
                response.text,
            )
            return False

        logger.info("Telegram message sent successfully")
        return True

    except requests.RequestException as ex:
        logger.exception(
            "Telegram send failed: %s",
            ex
        )
        return False
