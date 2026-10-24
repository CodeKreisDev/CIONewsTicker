"""Tests for ScoringService: scoring, filtering, and per-Artikel LLM resilience."""

from __future__ import annotations

from datetime import datetime, timezone

from cio_info_agent.application.ports.llm_port import LLMAntwortUngueltigError, LLMNichtErreichbarError
from cio_info_agent.application.services.scoring_service import ScoringService
from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.quelle import Quelle

_NOW = datetime(2026, 10, 24, 4, 0, tzinfo=timezone.utc)


class FakeLLMPort:
    """Returns pre-configured scores keyed by title, or raises a configured error."""

    def __init__(
        self,
        scores_je_titel: dict[str, int] | None = None,
        fehlerhafte_titel: dict[str, Exception] | None = None,
    ) -> None:
        self._scores_je_titel = scores_je_titel or {}
        self._fehlerhafte_titel = fehlerhafte_titel or {}

    def bewerte_relevanz(self, titel: str, beschreibung: str) -> int:
        if titel in self._fehlerhafte_titel:
            raise self._fehlerhafte_titel[titel]
        return self._scores_je_titel[titel]


class FakeArtikelRepository:
    """In-memory repository supporting the subset ScoringService needs."""

    def __init__(self, artikel_liste: list[Artikel]) -> None:
        self._artikel_je_id = {artikel.id: artikel for artikel in artikel_liste}

    def lies_alle_mit_status(self, status: ArtikelStatus) -> list[Artikel]:
        return [a for a in self._artikel_je_id.values() if a.status == status]

    def aktualisiere(self, artikel: Artikel) -> None:
        self._artikel_je_id[artikel.id] = artikel


def _eingegangener_artikel(titel: str, link: str) -> Artikel:
    return Artikel.eingegangen(
        quelle=Quelle.CIO_COM,
        link=link,
        titel=titel,
        veroeffentlicht_am=_NOW,
        eingegangen_am=_NOW,
    )


def test_relevant_artikel_stays_bewertet_as_a_candidate() -> None:
    artikel = _eingegangener_artikel("Critical BSI advisory", "https://example.com/1")
    repository = FakeArtikelRepository([artikel])
    service = ScoringService(FakeLLMPort(scores_je_titel={"Critical BSI advisory": 9}), repository)

    ergebnis = service.bewerte_und_filtere_alle()

    assert len(ergebnis.bewertete_artikel) == 1
    assert ergebnis.bewertete_artikel[0].status == ArtikelStatus.BEWERTET
    assert ergebnis.bewertete_artikel[0].relevanz_score.wert == 9
    assert ergebnis.verworfene_artikel == []


def test_non_relevant_artikel_is_discarded() -> None:
    artikel = _eingegangener_artikel("Unrelated gossip", "https://example.com/2")
    repository = FakeArtikelRepository([artikel])
    service = ScoringService(FakeLLMPort(scores_je_titel={"Unrelated gossip": 3}), repository)

    ergebnis = service.bewerte_und_filtere_alle()

    assert ergebnis.bewertete_artikel == []
    assert len(ergebnis.verworfene_artikel) == 1
    assert ergebnis.verworfene_artikel[0].status == ArtikelStatus.VERWORFEN


def test_llm_failure_for_one_artikel_does_not_block_the_others() -> None:
    failing = _eingegangener_artikel("Fails to score", "https://example.com/3")
    succeeding = _eingegangener_artikel("Scores fine", "https://example.com/4")
    repository = FakeArtikelRepository([failing, succeeding])
    service = ScoringService(
        FakeLLMPort(
            scores_je_titel={"Scores fine": 8},
            fehlerhafte_titel={"Fails to score": LLMNichtErreichbarError("down")},
        ),
        repository,
    )

    ergebnis = service.bewerte_und_filtere_alle()

    assert len(ergebnis.fehlgeschlagene_artikel) == 1
    assert ergebnis.fehlgeschlagene_artikel[0].titel == "Fails to score"
    assert len(ergebnis.bewertete_artikel) == 1
    assert ergebnis.bewertete_artikel[0].titel == "Scores fine"


def test_failed_artikel_remains_eingegangen_for_a_future_retry() -> None:
    artikel = _eingegangener_artikel("Fails to score", "https://example.com/5")
    repository = FakeArtikelRepository([artikel])
    service = ScoringService(
        FakeLLMPort(fehlerhafte_titel={"Fails to score": LLMAntwortUngueltigError("garbage")}),
        repository,
    )

    service.bewerte_und_filtere_alle()

    verbleibende = repository.lies_alle_mit_status(ArtikelStatus.EINGEGANGEN)
    assert len(verbleibende) == 1
    assert verbleibende[0].titel == "Fails to score"
