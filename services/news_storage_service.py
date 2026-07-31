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

        cursor = self.db.connection.cursor()


        for article in articles:


            title = article.get(
                "title",
                ""
            )


            link = article.get(
                "link",
                ""
            )


            if not title:

                continue



            unique_text = title + link


            news_hash = generate_hash(
                unique_text
            )



            cursor.execute(
                """
                SELECT id
                FROM news
                WHERE hash = ?
                """,
                (news_hash,)
            )


            exists = cursor.fetchone()


            if exists:

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
                    impact_score,
                    impact,
                    created_at
                )
                VALUES
                (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    link,
                    article.get(
                        "source",
                        ""
                    ),
                    article.get(
                        "category",
                        "GENERAL"
                    ),
                    article.get(
                        "published",
                        ""
                    ),
                    news_hash,
                    article.get(
                        "impact_score",
                        0
                    ),
                    article.get(
                        "impact",
                        "LOW"
                    ),
                    datetime.utcnow().isoformat()
                )
            )


            new_articles.append(
                article
            )



        self.db.connection.commit()


        logger.info(
            f"Saved {len(new_articles)} new articles"
        )


        return new_articles



    def close(self):

        self.db.close()
