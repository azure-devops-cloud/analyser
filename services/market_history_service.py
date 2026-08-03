from datetime import datetime, timezone

from services.database_service import DatabaseService


class MarketHistoryService:
    """Persist market observations and expose the latest snapshot comparison."""

    def __init__(self):
        self.db = DatabaseService()

    def record(self, instruments):
        captured_at = datetime.now(timezone.utc).isoformat()
        cursor = self.db.connection.cursor()

        for item in instruments:
            symbol = item.get("symbol") or item["name"]
            previous = cursor.execute(
                """
                SELECT price FROM market_history
                WHERE symbol = ?
                ORDER BY captured_at DESC
                LIMIT 1
                """,
                (symbol,),
            ).fetchone()
            previous_price = previous[0] if previous else None
            item["previous_snapshot_price"] = previous_price
            item["snapshot_change_pct"] = (
                round(((item["price"] - previous_price) / previous_price) * 100, 2)
                if previous_price
                else None
            )
            cursor.execute(
                """
                INSERT INTO market_history (
                    captured_at, name, symbol, price, daily_change,
                    trend, signal, rsi, volatility
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    captured_at,
                    item["name"],
                    symbol,
                    item["price"],
                    item.get("daily_change"),
                    item.get("trend"),
                    item.get("signal"),
                    item.get("rsi"),
                    item.get("volatility"),
                ),
            )

        self.db.connection.commit()
        return instruments

    def recent(self, limit=5):
        rows = self.db.connection.execute(
            """
            SELECT captured_at, name, symbol, price, daily_change, trend, signal
            FROM market_history
            ORDER BY captured_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        keys = ("captured_at", "name", "symbol", "price", "daily_change", "trend", "signal")
        return [dict(zip(keys, row)) for row in rows]

    def close(self):
        self.db.close()
