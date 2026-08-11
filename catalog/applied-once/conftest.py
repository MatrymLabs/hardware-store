"""Supply the reference adapter and a persistent backing location to contract tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent / "contract"))
sys.path.insert(0, str(Path(__file__).parent / "impl" / "python"))

from applied_once_impl import SqliteAppliedOnce


@pytest.fixture
def store_factory(tmp_path: Path):
    """Return fresh store objects that share one durable SQLite database."""
    database_path = tmp_path / "applied-once.sqlite3"

    def factory() -> SqliteAppliedOnce:
        return SqliteAppliedOnce(database_path)

    return factory


@pytest.fixture
def store(store_factory):
    """The implementation under contract."""
    return store_factory()
