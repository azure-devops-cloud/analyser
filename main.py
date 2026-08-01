import argparse
import os
import sys

from services.database_service import DatabaseService
from services.telegram_service import send_message
from services.logger import get_logger

from agents.manager_agent import ManagerAgent


logger = get_logger()


def build_report(results, table_count):
    message = [
        "🚀 MarketMind AI",
        "",
        "📊 Executive Brief",
        ""
    ]

    summary_result = None

    for result in results:
        if result.agent == "summary_agent" and result.status == "success":
            summary_result = result
            break

    if summary_result:
        message.append(summary_result.data.get("headline", "Executive view unavailable."))
        message.append("")
        message.append(summary_result.data.get("summary", "Summary unavailable."))
    else:
        top_market = None
        top_news = None

        for result in results:
            if result.status != "success":
                continue

            if result.agent == "market_agent" and result.data:
                top_market = result.data[0]

            if result.agent == "news_agent" and result.data:
                top_news = result.data["analysis"]

        if top_market:
            message.append(
                f"Lead: {top_market.get('name', 'N/A')} | Trend: {top_market.get('trend', 'N/A')} | Signal: {top_market.get('signal', 'N/A')}"
            )
        else:
            message.append("Lead: N/A | Trend: N/A | Signal: N/A")

        if top_news:
            message.append(
                f"News flow: {top_news.get('categories', {})} | Impact: {top_news.get('impact', {})}"
            )

    message.append("")
    message.extend([
        "💾 Database",
        f"Tables : {table_count}",
        "",
        "Status : Healthy ✅"
    ])

    return "\n".join(message)


def main(argv=None):
    parser = argparse.ArgumentParser(description="MarketMind AI")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the report without sending it to Telegram"
    )
    args = parser.parse_args(argv)

    logger.info("Starting MarketMind AI")

    # Initialize Database
    db = DatabaseService()
    db.initialize()
    tables = db.health_check()

    # Run all agents
    manager = ManagerAgent()
    results, context = manager.run()

    report = build_report(results, len(tables))

    if args.dry_run:
        print(report)
        db.close()
        logger.info("MarketMind AI completed in dry-run mode")
        return 0

    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

    if not token or not chat_id:
        db.close()
        logger.error(
            "Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
        )
        print(
            "Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
            file=sys.stderr,
        )
        return 1

    send_message(report)

    db.close()

    logger.info("MarketMind AI completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
