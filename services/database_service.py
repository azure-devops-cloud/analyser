import sqlite3
from pathlib import Path

from config.settings import DATABASE_PATH
from services.logger import get_logger


logger = get_logger(__name__)


class DatabaseService:


    def __init__(self):

        self.connection = sqlite3.connect(
            DATABASE_PATH
        )


    def initialize(self):

        schema_file = (
            Path(__file__).resolve()
            .parent.parent
            / "database"
            / "schema.sql"
        )


        with open(schema_file, "r", encoding="utf-8") as file:

            self.connection.executescript(
                file.read()
            )


        self.run_migrations()


        self.connection.commit()


        logger.info(
            "Database initialized"
        )


    def run_migrations(self):

        cursor = self.connection.cursor()


        cursor.execute(
            "PRAGMA table_info(news)"
        )


        columns = [
            row[1]
            for row in cursor.fetchall()
        ]


        if "impact_score" not in columns:

            logger.info(
                "Adding impact_score column"
            )

            cursor.execute(
                """
                ALTER TABLE news
                ADD COLUMN impact_score INTEGER DEFAULT 0
                """
            )


        if "impact" not in columns:

            logger.info(
                "Adding impact column"
            )

            cursor.execute(
                """
                ALTER TABLE news
                ADD COLUMN impact TEXT DEFAULT 'LOW'
                """
            )


    def health_check(self):

        cursor = self.connection.cursor()


        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """
        )


        return cursor.fetchall()



    def close(self):

        self.connection.close()
