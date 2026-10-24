"""Integration test for ArtikelRepository against a real SQLite file."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.quelle import Quelle
from cio_info_agent.infrastructure.persistence.connection import create_connection
from cio_info_agent.infrastructure.persistence.artikel_repository import ArtikelRepository


def test_speichere_and_existiert_round_trip(tmp_path: Path) -> None:
    connection = create_connection(tmp_path / "artikel.db")
    try:
        repository = ArtikelRepository(connection)
        artikel = Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/round-trip",
            titel="Round trip",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc),
        )

        assert not repository.existiert(artikel.id)

        repository.speichere(artikel)

        assert repository.existiert(artikel.id)

        wiedergelesen = repository.lies(artikel.id)
        assert wiedergelesen is not None
        assert wiedergelesen.link == artikel.link
        assert wiedergelesen.titel == artikel.titel
        assert wiedergelesen.quelle == artikel.quelle
        assert wiedergelesen.status == artikel.status
    finally:
        connection.close()


def test_repository_survives_reopening_the_same_database(tmp_path: Path) -> None:
    db_path = tmp_path / "persist.db"

    first_connection = create_connection(db_path)
    artikel = Artikel.eingegangen(
        quelle=Quelle.BITKOM,
        link="https://example.com/persisted",
        titel="Persisted",
        veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
    )
    ArtikelRepository(first_connection).speichere(artikel)
    first_connection.close()

    second_connection = create_connection(db_path)
    try:
        repository = ArtikelRepository(second_connection)
        assert repository.existiert(artikel.id)
    finally:
        second_connection.close()


def test_speichere_is_idempotent_on_duplicate_insert(tmp_path: Path) -> None:
    # Regression test: a concurrent writer (AD-5: batch + a future listener
    # share this database) could insert the same Artikel between another
    # caller's existiert() check and its own speichere() call. speichere()
    # must tolerate that race rather than raise.
    connection = create_connection(tmp_path / "race.db")
    try:
        repository = ArtikelRepository(connection)
        artikel = Artikel.eingegangen(
            quelle=Quelle.PROPMODO,
            link="https://example.com/raced",
            titel="Raced",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        )

        repository.speichere(artikel)
        repository.speichere(artikel)  # must not raise

        assert repository.existiert(artikel.id)
    finally:
        connection.close()
