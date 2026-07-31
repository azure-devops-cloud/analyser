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


        self.connection.commit()

        logger.info(
            "Database initialized"
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
