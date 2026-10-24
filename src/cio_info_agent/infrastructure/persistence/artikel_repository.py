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
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS artikel (
    id TEXT PRIMARY KEY,
    quelle TEXT NOT NULL,
    link TEXT NOT NULL,
    titel TEXT NOT NULL,
    beschreibung TEXT NOT NULL DEFAULT '',
    veroeffentlicht_am TEXT NOT NULL,
    eingegangen_am TEXT NOT NULL,
    status TEXT NOT NULL,
    relevanz_score INTEGER
)
"""

_SELECT_COLUMNS = (
    "quelle, link, titel, beschreibung, veroeffentlicht_am, eingegangen_am, status, relevanz_score"
)


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
                INSERT INTO artikel
                    (id, quelle, link, titel, beschreibung, veroeffentlicht_am, eingegangen_am, status, relevanz_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artikel.id.wert,
                    artikel.quelle.value,
                    artikel.link,
                    artikel.titel,
                    artikel.beschreibung,
                    artikel.veroeffentlicht_am.isoformat(),
                    artikel.eingegangen_am.isoformat(),
                    artikel.status.value,
                    artikel.relevanz_score.wert if artikel.relevanz_score else None,
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

    def aktualisiere(self, artikel: Artikel) -> None:
        """Persist a state transition (status and/or relevanz_score) for an
        already-stored Artikel.

        Raises:
            ValueError: if no stored Artikel with this id exists — this is a
                programming error (updating something never persisted), not
                a business-rule violation, so it fails fast with a plain
                exception rather than silently no-op'ing.
        """
        cursor = self._connection.execute(
            "UPDATE artikel SET status = ?, relevanz_score = ? WHERE id = ?",
            (
                artikel.status.value,
                artikel.relevanz_score.wert if artikel.relevanz_score else None,
                artikel.id.wert,
            ),
        )
        self._connection.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"No stored Artikel found with id {artikel.id.wert!r} to update.")

    def lies_alle_mit_status(self, status: ArtikelStatus) -> list[Artikel]:
        cursor = self._connection.execute(
            f"SELECT id, {_SELECT_COLUMNS} FROM artikel WHERE status = ?",
            (status.value,),
        )
        return [self._zu_artikel(row) for row in cursor.fetchall()]

    def lies(self, artikel_id: ArtikelId) -> Artikel | None:
        """Read back a stored Artikel by id (used by tests for round-tripping)."""
        cursor = self._connection.execute(
            f"SELECT id, {_SELECT_COLUMNS} FROM artikel WHERE id = ?",
            (artikel_id.wert,),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._zu_artikel(row)

    @staticmethod
    def _zu_artikel(row: tuple) -> Artikel:
        (
            artikel_id,
            quelle,
            link,
            titel,
            beschreibung,
            veroeffentlicht_am,
            eingegangen_am,
            status,
            relevanz_score,
        ) = row
        return Artikel(
            id=ArtikelId(wert=artikel_id),
            quelle=Quelle(quelle),
            link=link,
            titel=titel,
            beschreibung=beschreibung,
            veroeffentlicht_am=_parse_iso(veroeffentlicht_am),
            eingegangen_am=_parse_iso(eingegangen_am),
            status=ArtikelStatus(status),
            relevanz_score=RelevanzScore(relevanz_score) if relevanz_score is not None else None,
        )


def _parse_iso(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
