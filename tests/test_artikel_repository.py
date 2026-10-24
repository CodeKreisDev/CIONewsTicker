"""Integration test for ArtikelRepository against a real SQLite file."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.quelle import Quelle
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore
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
            beschreibung="Some description",
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
        assert wiedergelesen.beschreibung == "Some description"
        assert wiedergelesen.relevanz_score is None
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


def test_aktualisiere_persists_status_and_relevanz_score(tmp_path: Path) -> None:
    connection = create_connection(tmp_path / "aktualisiere.db")
    try:
        repository = ArtikelRepository(connection)
        artikel = Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/to-score",
            titel="To score",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        )
        repository.speichere(artikel)

        bewerteter = artikel.bewerte(RelevanzScore(8))
        repository.aktualisiere(bewerteter)

        wiedergelesen = repository.lies(artikel.id)
        assert wiedergelesen is not None
        assert wiedergelesen.status == ArtikelStatus.BEWERTET
        assert wiedergelesen.relevanz_score == RelevanzScore(8)
    finally:
        connection.close()


def test_aktualisiere_raises_when_artikel_does_not_exist(tmp_path: Path) -> None:
    connection = create_connection(tmp_path / "missing.db")
    try:
        repository = ArtikelRepository(connection)
        nie_gespeichert = Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/never-saved",
            titel="Never saved",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        )

        with pytest.raises(ValueError):
            repository.aktualisiere(nie_gespeichert)
    finally:
        connection.close()


def test_lies_alle_mit_status_returns_only_matching_artikel(tmp_path: Path) -> None:
    connection = create_connection(tmp_path / "status-query.db")
    try:
        repository = ArtikelRepository(connection)
        eingegangener = Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/still-eingegangen",
            titel="Still eingegangen",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        )
        bewerteter_roh = Artikel.eingegangen(
            quelle=Quelle.BITKOM,
            link="https://example.com/already-bewertet",
            titel="Already bewertet",
            veroeffentlicht_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
            eingegangen_am=datetime(2026, 10, 24, tzinfo=timezone.utc),
        )
        repository.speichere(eingegangener)
        repository.speichere(bewerteter_roh)
        repository.aktualisiere(bewerteter_roh.bewerte(RelevanzScore(9)))

        nur_eingegangen = repository.lies_alle_mit_status(ArtikelStatus.EINGEGANGEN)

        assert [a.id for a in nur_eingegangen] == [eingegangener.id]
    finally:
        connection.close()
