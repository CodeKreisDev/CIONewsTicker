"""Tests for the Artikel aggregate: factory and deterministic identity."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.quelle import Quelle


def test_eingegangen_creates_artikel_in_eingegangen_status() -> None:
    now = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)

    artikel = Artikel.eingegangen(
        quelle=Quelle.BSI,
        link="https://example.com/a",
        titel="Some title",
        veroeffentlicht_am=now,
        eingegangen_am=now,
    )

    assert artikel.status == ArtikelStatus.EINGEGANGEN
    assert artikel.quelle == Quelle.BSI
    assert artikel.link == "https://example.com/a"


def test_same_quelle_and_link_produce_same_artikel_id() -> None:
    id_a = ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/x")
    id_b = ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/x")

    assert id_a == id_b


def test_different_link_produces_different_artikel_id() -> None:
    id_a = ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/x")
    id_b = ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/y")

    assert id_a != id_b


def test_different_quelle_produces_different_artikel_id() -> None:
    id_a = ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/x")
    id_b = ArtikelId.von_quelle_und_link(Quelle.BITKOM, "https://example.com/x")

    assert id_a != id_b


def test_eingegangen_derives_id_from_quelle_and_link() -> None:
    now = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)

    artikel = Artikel.eingegangen(
        quelle=Quelle.PROPMODO,
        link="https://example.com/z",
        titel="Title",
        veroeffentlicht_am=now,
        eingegangen_am=now,
    )

    assert artikel.id == ArtikelId.von_quelle_und_link(Quelle.PROPMODO, "https://example.com/z")


def test_eingegangen_rejects_naive_veroeffentlicht_am() -> None:
    naive = datetime(2026, 10, 24, 4, 0)  # no tzinfo
    aware = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="veroeffentlicht_am"):
        Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/naive",
            titel="Title",
            veroeffentlicht_am=naive,
            eingegangen_am=aware,
        )


def test_eingegangen_rejects_naive_eingegangen_am() -> None:
    naive = datetime(2026, 10, 24, 4, 0)  # no tzinfo
    aware = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)

    with pytest.raises(ValueError, match="eingegangen_am"):
        Artikel.eingegangen(
            quelle=Quelle.CIO_COM,
            link="https://example.com/naive2",
            titel="Title",
            veroeffentlicht_am=aware,
            eingegangen_am=naive,
        )
