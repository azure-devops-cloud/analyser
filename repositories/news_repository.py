from typing import Any, Dict, List

from services.database_service import DatabaseService


class NewsRepository:
    """Repository wrapper for storing and querying processed news records."""

    def __init__(self):
        self.db = DatabaseService()

    def save(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        cursor = self.db.connection.cursor()
        saved: List[Dict[str, Any]] = []

        for article in articles:
            cursor.execute(
                """
                INSERT OR IGNORE INTO news (
                    title,
                    url,
                    source,
                    category,
                    published_at,
                    hash,
                    impact_score,
                    impact,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (
                    article.get("title", ""),
                    article.get("link", ""),
                    article.get("source", ""),
                    article.get("category", "GENERAL"),
                    article.get("published", ""),
                    article.get("hash", article.get("title", "") + article.get("link", "")),
                    article.get("impact_score", 0),
                    article.get("impact", "LOW"),
                ),
            )
            if cursor.rowcount > 0:
                saved.append(article)

        self.db.connection.commit()
        return saved

    def close(self) -> None:
        self.db.close()
