import os
import requests

from config import settings
from services.logger import get_logger

logger = get_logger(__name__)


def send_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN", settings.TELEGRAM_BOT_TOKEN)
    chat_id = os.getenv("TELEGRAM_CHAT_ID", settings.TELEGRAM_CHAT_ID)

    if not token or not chat_id:
        logger.warning(
            "Telegram credentials are not configured; skipping message send."
        )
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    response = requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": message
        },
        timeout=30
    )

    if response.status_code >= 400:
        logger.warning(
            "Telegram message send failed: %s",
            response.text
        )
        return False

    logger.info("Telegram message sent successfully")
    return True
