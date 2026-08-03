from datetime import datetime, timezone

from services.database_service import DatabaseService


class AlertService:
    """Store one actionable watch alert per asset, direction, and UTC day."""

    def __init__(self):
        self.db = DatabaseService()

    def create_actionable_alerts(self, decisions):
        today = datetime.now(timezone.utc).date().isoformat()
        cursor = self.db.connection.cursor()
        created = []

        for decision in decisions:
            bias = decision.get("bias")
            score = decision.get("score", 0)
            if bias == "BULLISH" and score >= 80:
                direction = "BUY_WATCH"
            elif bias == "BEARISH" and score <= 35:
                direction = "SELL_WATCH"
            else:
                continue

            name = decision["name"]
            fingerprint = f"{today}:{name}:{direction}"
            message = (
                f"{direction}: {name} scored {score}/100 "
                f"({decision.get('trend', 'UNKNOWN')} trend, RSI {decision.get('rsi', 'N/A')})."
            )
            cursor.execute(
                """
                INSERT OR IGNORE INTO alerts (category, message, fingerprint, sent)
                VALUES (?, ?, ?, 0)
                """,
                (direction, message, fingerprint),
            )
            if cursor.rowcount:
                created.append({"category": direction, "message": message})

        self.db.connection.commit()
        return created

    def close(self):
        self.db.close()
