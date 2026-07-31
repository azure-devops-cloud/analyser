from datetime import datetime
from services.telegram_service import send_message

message = f"""
🚀 MarketMind AI

Status: Online

GitHub Actions: SUCCESS

Time:
{datetime.utcnow()} UTC

This message was sent automatically.
"""

send_message(message)
