import argparse
import json
import os
import sys
import time

from services.database_service import DatabaseService
from services.telegram_service import TELEGRAM_FAILED, TELEGRAM_SENT, send_message, send_message_status
from services.logger import get_logger
from agents.manager_agent import ManagerAgent

logger = get_logger()


def build_report(results, table_count):
    message = ["🚀 MarketMind AI", "", "📊 Executive Brief", ""]
    summary_result = next((r for r in results if r.agent == "summary_agent" and r.status == "success"), None)
    if summary_result:
        data = summary_result.data
        message.append(data.get("headline", "Executive view unavailable."))
        message.append("")
        message.append(f"Lead: {data.get('top_opportunity', 'N/A')} | Posture: {data.get('market_posture', 'Neutral')}")
        message.append(f"Risk: {data.get('risk_watch', data.get('risk_caveat', 'Risk unavailable.'))}")
        message.append(f"Action: {data.get('action_recommendation', 'Action unavailable.')}")
        alerts = data.get("alerts", [])
        if alerts:
            message.append(f"Alert: {alerts[0].get('message', 'Actionable alert available.')}")
    else:
        top_market = next((r.data[0] for r in results if r.agent == "market_agent" and r.status == "success" and r.data), None)
        if top_market:
            message.append(f"Lead: {top_market.get('name', 'N/A')} | Trend: {top_market.get('trend', 'N/A')} | Signal: {top_market.get('signal', 'N/A')}")
            message.append("Risk: watch momentum and confirmation before adding exposure.")
            message.append(f"Action: maintain selective exposure in {top_market.get('name', 'N/A')}")
        else:
            message.append("Lead: N/A | Trend: N/A | Signal: N/A")
            message.append("Risk: data unavailable")
            message.append("Action: hold and wait")
    message.extend(["", "💾 Database", f"Tables : {table_count}", "", "Status : Healthy ✅"])
    return "\n".join(message)


def build_report_payload(results, table_count):
    summary = next((r.data for r in results if r.agent == "summary_agent" and r.status == "success"), {})
    agent_status = {r.agent: {"status": r.status, "count": r.count, "errors": r.errors} for r in results}
    failed_agents = [name for name, result in agent_status.items() if result["status"] != "success"]
    return {"application": "MarketMind AI", "workflow_health": "healthy" if not failed_agents else "degraded", "failed_agents": failed_agents, "database": {"table_count": table_count}, "executive_brief": summary, "agents": agent_status}


def main(argv=None):
    parser = argparse.ArgumentParser(description="MarketMind AI")
    parser.add_argument("--dry-run", action="store_true", help="Generate the report without sending it to Telegram")
    parser.add_argument("--format", choices=("text", "json"), default="text", help="Report format for --dry-run output")
    parser.add_argument("--loop", action="store_true", help="Run the workflow repeatedly in a bounded loop")
    parser.add_argument("--max-runs", type=int, default=1, help="Number of loop iterations to execute when --loop is enabled")
    parser.add_argument("--interval", type=float, default=60.0, help="Seconds to wait between loop iterations")
    args = parser.parse_args(argv)
    if args.loop and args.max_runs < 1:
        parser.error("--max-runs must be at least 1 when --loop is enabled")
    if args.loop and args.interval < 0:
        parser.error("--interval must be zero or greater")
    if args.format == "json" and not args.dry_run:
        parser.error("--format json is available only with --dry-run")
    logger.info("Starting MarketMind AI")
    db = DatabaseService()
    db.initialize()
    tables = db.health_check()
    loop_runs = args.max_runs if args.loop else 1
    try:
        for run_index in range(loop_runs):
            manager = ManagerAgent()
            results, context = manager.run()
            text_report = build_report(results, len(tables))
            report = json.dumps(build_report_payload(results, len(tables)), indent=2) if args.format == "json" else text_report
            if args.dry_run:
                print(report)
            else:
                token = os.getenv("TELEGRAM_BOT_TOKEN", "")
                chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
                if not token or not chat_id:
                    logger.error("Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
                    print("Live Telegram delivery requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID", file=sys.stderr)
                    return 1
                confidence = None
                actionable_alerts = []
                for result in results:
                    if result.agent == "summary_agent" and result.status == "success":
                        confidence = result.data.get("fact_validation", {}).get("confidence_score")
                    if result.agent == "alert_agent" and result.status == "success":
                        actionable_alerts = result.data.get("alerts", [])
                delivery_confidence = None if actionable_alerts else confidence
                status = send_message_status(text_report, confidence_score=delivery_confidence, threshold=80)
                if status == TELEGRAM_FAILED:
                    logger.error("Telegram report delivery failed")
                    return 1
                if status != TELEGRAM_SENT:
                    logger.info("Telegram report delivery skipped")
            if args.loop and run_index < loop_runs - 1 and args.interval > 0:
                time.sleep(args.interval)
        logger.info("MarketMind AI completed in dry-run mode" if args.dry_run else "MarketMind AI completed")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
