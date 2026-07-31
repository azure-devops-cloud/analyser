from datetime import datetime

from services.database_service import DatabaseService
from services.hash_service import generate_hash
from services.logger import get_logger


logger = get_logger(__name__)


class NewsStorageService:

    def __init__(self):
        self.db = DatabaseService()


    def save_news(self, articles):

        new_articles = []

        connection = self.db.connection

        cursor = connection.cursor()


        for article in articles:

            title = article.get("title", "")

            if not title:
                continue


            news_hash = generate_hash(title)


            cursor.execute(
                """
                SELECT id
                FROM news
                WHERE hash = ?
                """,
                (news_hash,)
            )


            existing = cursor.fetchone()


            if existing:
                continue


            cursor.execute(
                """
                INSERT INTO news
                (
                    title,
                    url,
                    source,
                    category,
                    published_at,
                    hash,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    article.get("link"),
                    article.get("source", ""),
                    article.get("category", "unknown"),
                    article.get("published", ""),
                    news_hash,
                    datetime.utcnow().isoformat()
                )
            )


            new_articles.append(article)


        connection.commit()


        logger.info(
            f"Saved {len(new_articles)} new articles"
        )


        return new_articles


    def close(self):

        self.db.close()
