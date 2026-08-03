import argparse
import os
import sys
import time

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
        data = summary_result.data
        headline = data.get("headline", "Executive view unavailable.")
        action = data.get("action_recommendation", "Action unavailable.")
        risk = data.get("risk_watch", data.get("risk_caveat", "Risk unavailable."))
        lead = data.get("top_opportunity", "N/A")
        posture = data.get("market_posture", "Neutral")

        message.append(f"{headline}")
        message.append("")
        message.append(f"Lead: {lead} | Posture: {posture}")
        message.append(f"Risk: {risk}")
        message.append(f"Action: {action}")
    else:
        top_market = None

        for result in results:
            if result.status != "success":
                continue

            if result.agent == "market_agent" and result.data:
                top_market = result.data[0]
                break

        if top_market:
            message.append(
                f"Lead: {top_market.get('name', 'N/A')} | Trend: {top_market.get('trend', 'N/A')} | Signal: {top_market.get('signal', 'N/A')}"
            )
            message.append(
                f"Risk: watch momentum and confirmation before adding exposure."
            )
            message.append(
                f"Action: maintain selective exposure in {top_market.get('name', 'N/A')}"
            )
        else:
            message.append("Lead: N/A | Trend: N/A | Signal: N/A")
            message.append("Risk: data unavailable")
            message.append("Action: hold and wait")

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
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run the workflow repeatedly in a bounded loop"
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=1,
        help="Number of loop iterations to execute when --loop is enabled"
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=60.0,
        help="Seconds to wait between loop iterations"
    )
    args = parser.parse_args(argv)

    if args.loop and args.max_runs < 1:
        parser.error("--max-runs must be at least 1 when --loop is enabled")

    if args.loop and args.interval < 0:
        parser.error("--interval must be zero or greater")

    logger.info("Starting MarketMind AI")

    # Initialize Database
    db = DatabaseService()
    db.initialize()
    tables = db.health_check()

    loop_runs = args.max_runs if args.loop else 1

    try:
        for run_index in range(loop_runs):
            manager = ManagerAgent()
            results, context = manager.run()
            report = build_report(results, len(tables))

            if args.dry_run:
                print(report)
            else:
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                chat_id = os.getenv("TELEGRAM_CHAT_ID", "")

                if not token or not chat_id:
                    logger.error(
                        "Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID"
                    )
                    print(
                        "Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID",
                        file=sys.stderr,
                    )
                    return 1

                confidence = None
                for result in results:
                    if result.agent == "summary_agent" and result.status == "success":
                        confidence = result.data.get("fact_validation", {}).get("confidence_score")
                        break

                send_message(report, confidence_score=confidence, threshold=80)

            if args.loop and run_index < loop_runs - 1 and args.interval > 0:
                time.sleep(args.interval)

        logger.info("MarketMind AI completed in dry-run mode" if args.dry_run else "MarketMind AI completed")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
