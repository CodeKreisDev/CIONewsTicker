"""Orchestrates relevance scoring and filtering across all EINGEGANGEN Artikel.

Per-Artikel resilience (a failed LLM call never blocks the remaining Artikel)
mirrors the per-source resilience in IngestionService — the same robustness
principle (NFR: "Ausfall darf übrige nicht blockieren") applied one layer
further in the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cio_info_agent.application.ports.artikel_repository_port import ArtikelRepositoryPort
from cio_info_agent.application.ports.llm_port import (
    LLMAntwortUngueltigError,
    LLMNichtErreichbarError,
    LLMPort,
)
from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.exception.ungueltiger_relevanz_score_error import (
    UngueltigerRelevanzScoreError,
)
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore


@dataclass(frozen=True)
class ScoringErgebnis:
    """Outcome of one scoring-and-filtering run."""

    bewertete_artikel: list[Artikel] = field(default_factory=list)
    verworfene_artikel: list[Artikel] = field(default_factory=list)
    fehlgeschlagene_artikel: list[Artikel] = field(default_factory=list)


class ScoringService:
    """Scores every EINGEGANGEN Artikel and filters out non-relevant ones."""

    def __init__(self, llm_port: LLMPort, repository: ArtikelRepositoryPort) -> None:
        self._llm_port = llm_port
        self._repository = repository

    def bewerte_und_filtere_alle(self) -> ScoringErgebnis:
        """Score and filter every Artikel currently in the EINGEGANGEN state.

        A failed scoring attempt (unreachable LLM or an unparseable
        response) leaves that single Artikel in EINGEGANGEN — it is retried
        on a future run — and does not prevent the remaining Artikel from
        being scored (FR3, FR4).
        """
        bewertete_artikel: list[Artikel] = []
        verworfene_artikel: list[Artikel] = []
        fehlgeschlagene_artikel: list[Artikel] = []

        eingegangene_artikel = self._repository.lies_alle_mit_status(ArtikelStatus.EINGEGANGEN)

        for artikel in eingegangene_artikel:
            try:
                score_wert = self._llm_port.bewerte_relevanz(artikel.titel, artikel.beschreibung)
                score = RelevanzScore(score_wert)
            except (LLMNichtErreichbarError, LLMAntwortUngueltigError, UngueltigerRelevanzScoreError):
                # A defensive catch for UngueltigerRelevanzScoreError: it
                # guards against any LLMPort implementation that fails to
                # validate its own 1-10 range before returning — not just
                # OpenAILLMAdapter, which already validates internally.
                fehlgeschlagene_artikel.append(artikel)
                continue

            bewerteter_artikel = artikel.bewerte(score)

            if score.ist_relevant():
                self._repository.aktualisiere(bewerteter_artikel)
                bewertete_artikel.append(bewerteter_artikel)
            else:
                verworfener_artikel = bewerteter_artikel.verwerfen()
                self._repository.aktualisiere(verworfener_artikel)
                verworfene_artikel.append(verworfener_artikel)

        return ScoringErgebnis(
            bewertete_artikel=bewertete_artikel,
            verworfene_artikel=verworfene_artikel,
            fehlgeschlagene_artikel=fehlgeschlagene_artikel,
        )
