from database.unit_of_work import SQLiteUnitOfWork
from services.database_service import DatabaseService


def test_database_enables_reliability_pragmas_and_metric_schema(tmp_path):
    database = DatabaseService(tmp_path / "marketmind.db")

    foreign_keys = database.connection.execute("PRAGMA foreign_keys").fetchone()[0]
    busy_timeout = database.connection.execute("PRAGMA busy_timeout").fetchone()[0]
    tables = {row[0] for row in database.health_check()}
    database.close()

    assert foreign_keys == 1
    assert busy_timeout == 5000
    assert {"schema_migrations", "execution_metrics"}.issubset(tables)


def test_unit_of_work_rolls_back_failed_transaction(tmp_path):
    database = DatabaseService(tmp_path / "marketmind.db")
    try:
        with SQLiteUnitOfWork(database) as unit_of_work:
            unit_of_work.connection.execute(
                "INSERT INTO alerts (category, message, fingerprint) VALUES (?, ?, ?)",
                ("TEST", "rollback", "test-rollback"),
            )
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass

    verify = DatabaseService(tmp_path / "marketmind.db")
    count = verify.connection.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    verify.close()

    assert count == 0
