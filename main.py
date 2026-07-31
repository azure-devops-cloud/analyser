from services.database_service import DatabaseService
from services.telegram_service import send_message
from services.logger import get_logger
from agents.news_agent import NewsAgent

logger = get_logger()

logger.info("Starting MarketMind AI")

db = DatabaseService()

db.initialize()

tables = db.health_check()

message = f"""
🚀 MarketMind AI

Database initialized successfully.

Tables created:

{len(tables)}

Status

Healthy ✅
"""

send_message(message)

db.close()

logger.info("Execution completed.")

agent = NewsAgent()

articles = agent.run()

print(f"Collected {len(articles)} articles")
