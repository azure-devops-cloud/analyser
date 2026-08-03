import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from services.logger import get_logger


logger = get_logger(__name__)


class DatabaseService:
    """Own a configured SQLite connection and apply schema migrations."""

    def __init__(self, database_path: Path | None = None):
        self.database_path = database_path or DATABASE_PATH
        self.connection = sqlite3.connect(self.database_path, timeout=5.0)
        self.connection.row_factory = sqlite3.Row
        self._configure_connection()

        self.initialize()

    def _configure_connection(self) -> None:
        """Apply settings that make short-lived concurrent runs safer."""
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")

    def initialize(self) -> None:

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

        self.connection.execute(
            "INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)",
            ("2026-08-phase-1",),
        )


        self.connection.commit()


        logger.info(
            "Database initialized"
        )


    def run_migrations(self) -> None:

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

        cursor.execute("PRAGMA table_info(alerts)")
        alert_columns = [row[1] for row in cursor.fetchall()]
        if "fingerprint" not in alert_columns:
            cursor.execute("ALTER TABLE alerts ADD COLUMN fingerprint TEXT")
            cursor.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_alerts_fingerprint "
                "ON alerts (fingerprint)"
            )


    def health_check(self) -> list[sqlite3.Row]:

        cursor = self.connection.cursor()


        cursor.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """
        )


        return cursor.fetchall()



    def close(self) -> None:

        self.connection.close()
