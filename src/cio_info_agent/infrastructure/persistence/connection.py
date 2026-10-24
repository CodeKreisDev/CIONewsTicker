"""SQLite connection factory, ensuring WAL mode is enabled (AD-7)."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class WalModeUnavailableError(RuntimeError):
    """Raised when SQLite accepted the connection but did not enable WAL mode."""


def create_connection(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection and enable WAL (Write-Ahead Logging) mode.

    Creates the parent directory of `db_path` if it does not exist yet, so the
    very first run does not fail with "unable to open database file".

    Args:
        db_path: Filesystem path to the SQLite database file.

    Returns:
        An open sqlite3.Connection with `journal_mode=WAL` active.

    Raises:
        WalModeUnavailableError: if the filesystem does not support WAL mode
            (e.g. some network/mounted volumes), so the AD-7 invariant is
            surfaced instead of silently ignored.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(str(path))
    (journal_mode,) = connection.execute("PRAGMA journal_mode=WAL").fetchone()
    if journal_mode.lower() != "wal":
        connection.close()
        raise WalModeUnavailableError(
            f"Expected WAL journal mode, got '{journal_mode}' for {path}."
        )
    return connection
