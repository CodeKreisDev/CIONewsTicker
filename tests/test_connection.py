"""Tests for create_connection: WAL mode, auto-created data directory."""

from __future__ import annotations

from pathlib import Path

from cio_info_agent.infrastructure.persistence.connection import create_connection


def test_create_connection_enables_wal_mode(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    connection = create_connection(db_path)
    try:
        cursor = connection.execute("PRAGMA journal_mode")
        (journal_mode,) = cursor.fetchone()
    finally:
        connection.close()

    assert journal_mode.lower() == "wal"


def test_create_connection_creates_missing_parent_directory(tmp_path: Path) -> None:
    db_path = tmp_path / "data" / "nested" / "test.db"
    assert not db_path.parent.exists()

    connection = create_connection(db_path)
    try:
        assert db_path.parent.is_dir()
    finally:
        connection.close()
