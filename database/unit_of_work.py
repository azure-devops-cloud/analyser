"""Transaction boundary for repositories that share one SQLite connection."""

from types import TracebackType
from typing import Optional, Type

from services.database_service import DatabaseService


class SQLiteUnitOfWork:
    """Commit on success and roll back automatically when a block fails."""

    def __init__(self, database_service: Optional[DatabaseService] = None) -> None:
        self.database_service = database_service or DatabaseService()

    @property
    def connection(self):
        """Expose the transaction-scoped database connection to repositories."""
        return self.database_service.connection

    def __enter__(self) -> "SQLiteUnitOfWork":
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if exception_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.database_service.close()
