"""SQLite implementation of ArtikelRepositoryPort.

Uses the WAL-mode connection factory from Story 1.1 (AD-7) so this repository
is safe to use from both the batch and listener processes described in the
Architecture Spine (AD-5).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.quelle import Quelle

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS artikel (
    id TEXT PRIMARY KEY,
    quelle TEXT NOT NULL,
    link TEXT NOT NULL,
    titel TEXT NOT NULL,
    veroeffentlicht_am TEXT NOT NULL,
    eingegangen_am TEXT NOT NULL,
    status TEXT NOT NULL
)
"""


class ArtikelRepository:
    """Persists Artikel aggregates in a SQLite table, keyed by ArtikelId."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._connection.execute(_CREATE_TABLE_SQL)
        self._connection.commit()

    def existiert(self, artikel_id: ArtikelId) -> bool:
        cursor = self._connection.execute(
            "SELECT 1 FROM artikel WHERE id = ?", (artikel_id.wert,)
        )
        return cursor.fetchone() is not None

    def speichere(self, artikel: Artikel) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO artikel (id, quelle, link, titel, veroeffentlicht_am, eingegangen_am, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artikel.id.wert,
                    artikel.quelle.value,
                    artikel.link,
                    artikel.titel,
                    artikel.veroeffentlicht_am.isoformat(),
                    artikel.eingegangen_am.isoformat(),
                    artikel.status.value,
                ),
            )
            self._connection.commit()
        except sqlite3.IntegrityError:
            # Another process (per AD-5, the batch and a future listener
            # share this database) already inserted this exact Artikel
            # between our caller's existiert() check and this insert. That
            # is a benign race, not a failure — the record already exists as
            # intended, so roll back this no-op attempt and move on.
            self._connection.rollback()

    def lies(self, artikel_id: ArtikelId) -> Artikel | None:
        """Read back a stored Artikel by id (used by tests for round-tripping)."""
        cursor = self._connection.execute(
            "SELECT quelle, link, titel, veroeffentlicht_am, eingegangen_am, status "
            "FROM artikel WHERE id = ?",
            (artikel_id.wert,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        quelle, link, titel, veroeffentlicht_am, eingegangen_am, status = row
        return Artikel(
            id=artikel_id,
            quelle=Quelle(quelle),
            link=link,
            titel=titel,
            veroeffentlicht_am=_parse_iso(veroeffentlicht_am),
            eingegangen_am=_parse_iso(eingegangen_am),
            status=ArtikelStatus(status),
        )


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
