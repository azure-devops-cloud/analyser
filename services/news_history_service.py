from services.database_service import DatabaseService


class NewsHistoryService:
    """Query persisted news so reports can distinguish live from historical flow."""

    def __init__(self):
        self.db = DatabaseService()

    def summary(self, limit=5):
        cursor = self.db.connection.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM news").fetchone()[0]
        recent_count = cursor.execute(
            "SELECT COUNT(*) FROM news WHERE created_at >= datetime('now', '-1 day')"
        ).fetchone()[0]
        category_rows = cursor.execute(
            """
            SELECT category, COUNT(*)
            FROM news
            WHERE created_at >= datetime('now', '-1 day')
            GROUP BY category
            ORDER BY COUNT(*) DESC, category ASC
            """
        ).fetchall()
        headlines = cursor.execute(
            """
            SELECT title, source, category, published_at, created_at
            FROM news
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return {
            "total_articles": total,
            "articles_last_24h": recent_count,
            "categories_last_24h": dict(category_rows),
            "recent_headlines": [
                {
                    "title": row[0],
                    "source": row[1],
                    "category": row[2],
                    "published_at": row[3],
                    "stored_at": row[4],
                }
                for row in headlines
            ],
        }

    def close(self):
        self.db.close()
