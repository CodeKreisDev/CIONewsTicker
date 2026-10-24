"""Tests for Artikel.bewerte / Artikel.verwerfen: state transitions and the R1 invariant."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.exception.ungueltiger_zustandsuebergang_error import (
    UngueltigerZustandsuebergangError,
)
from cio_info_agent.domain.artikel.quelle import Quelle
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore

_NOW = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)


def _eingegangener_artikel() -> Artikel:
    return Artikel.eingegangen(
        quelle=Quelle.CIO_COM,
        link="https://example.com/a",
        titel="Title",
        veroeffentlicht_am=_NOW,
        eingegangen_am=_NOW,
    )


def test_bewerte_transitions_to_bewertet_and_records_score() -> None:
    artikel = _eingegangener_artikel()
    score = RelevanzScore(8)

    bewerteter = artikel.bewerte(score)

    assert bewerteter.status == ArtikelStatus.BEWERTET
    assert bewerteter.relevanz_score == score


def test_bewerte_raises_when_not_eingegangen() -> None:
    bewerteter = _eingegangener_artikel().bewerte(RelevanzScore(8))

    with pytest.raises(UngueltigerZustandsuebergangError):
        bewerteter.bewerte(RelevanzScore(5))


def test_verwerfen_transitions_to_verworfen_when_not_relevant() -> None:
    bewerteter = _eingegangener_artikel().bewerte(RelevanzScore(4))

    verworfener = bewerteter.verwerfen()

    assert verworfener.status == ArtikelStatus.VERWORFEN


def test_verwerfen_raises_when_score_is_still_relevant() -> None:
    bewerteter = _eingegangener_artikel().bewerte(RelevanzScore(7))

    with pytest.raises(UngueltigerZustandsuebergangError):
        bewerteter.verwerfen()


def test_verwerfen_raises_when_not_bewertet() -> None:
    artikel = _eingegangener_artikel()

    with pytest.raises(UngueltigerZustandsuebergangError):
        artikel.verwerfen()
