"""SQLite reference implementation of the durable applied-once contract."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from applied_once import KeyRefused


class SqliteAppliedOnce:
    """Use a unique durable row as the atomic exactly-once claim.

    Each method opens a short-lived SQLite connection. The database's unique primary key and
    ``INSERT OR IGNORE`` make competing processes contend on one atomic write instead of relying
    on an unsafe read followed by an insert.
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.execute(
                "CREATE TABLE IF NOT EXISTS applied_once (operation_key TEXT PRIMARY KEY)"
            )

    def seen(self, key: str) -> bool:
        """Return whether the durable record exists for ``key``."""
        self._validate_key(key)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM applied_once WHERE operation_key = ?", (key,)
            ).fetchone()
        return row is not None

    def claim(self, key: str) -> bool:
        """Atomically create the durable record for ``key`` when it is absent."""
        self._validate_key(key)
        with self._connect() as connection:
            result = connection.execute(
                "INSERT OR IGNORE INTO applied_once (operation_key) VALUES (?)", (key,)
            )
        return result.rowcount == 1

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._database_path)

    @staticmethod
    def _validate_key(key: str) -> None:
        if not isinstance(key, str) or not key.strip():
            raise KeyRefused("applied-once key must be a non-empty string")
