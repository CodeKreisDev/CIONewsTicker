"""Artikel aggregate root.

An Artikel is identified by its ArtikelId (derived from Quelle + Link) and
carries its own lifecycle state. Ingestion (Story 1.2) only ever produces an
Artikel in the EINGEGANGEN state via the `eingegangen` factory; `bewerte` and
`verwerfen` (Story 1.3) transition it onward through scoring and filtering.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime

from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.exception.ungueltiger_zustandsuebergang_error import (
    UngueltigerZustandsuebergangError,
)
from cio_info_agent.domain.artikel.quelle import Quelle
from cio_info_agent.domain.artikel.relevanz_score import RelevanzScore


@dataclass(frozen=True)
class Artikel:
    """Aggregate root for a single ingested news article.

    Frozen by design: an Artikel's recorded facts (id, source, link, title,
    timestamps) never change after ingestion. State transitions are modeled
    as producing a new, updated Artikel instance (via `bewerte`/`verwerfen`),
    not by mutating this one in place.
    """

    id: ArtikelId
    quelle: Quelle
    link: str
    titel: str
    veroeffentlicht_am: datetime
    eingegangen_am: datetime
    status: ArtikelStatus
    beschreibung: str = ""
    relevanz_score: RelevanzScore | None = None

    def __post_init__(self) -> None:
        # Fail-fast at the aggregate boundary (ddd-principles.md): a naive
        # datetime silently "becomes" UTC wherever it is later read back,
        # which is a correctness trap, not a convenience. Reject it here
        # instead of letting it surface far from where it was created.
        for feld_name in ("veroeffentlicht_am", "eingegangen_am"):
            wert = getattr(self, feld_name)
            if wert.tzinfo is None:
                raise ValueError(
                    f"Artikel.{feld_name} must be timezone-aware, got a naive datetime."
                )

    @classmethod
    def eingegangen(
        cls,
        quelle: Quelle,
        link: str,
        titel: str,
        veroeffentlicht_am: datetime,
        eingegangen_am: datetime,
        beschreibung: str = "",
    ) -> "Artikel":
        """Create a newly-ingested Artikel in the EINGEGANGEN state.

        This is the only way to construct an Artikel from outside the
        aggregate — it guarantees the id is always correctly derived from
        (quelle, link), never supplied independently.
        """
        return cls(
            id=ArtikelId.von_quelle_und_link(quelle, link),
            quelle=quelle,
            link=link,
            titel=titel,
            veroeffentlicht_am=veroeffentlicht_am,
            eingegangen_am=eingegangen_am,
            status=ArtikelStatus.EINGEGANGEN,
            beschreibung=beschreibung,
        )

    def bewerte(self, score: RelevanzScore) -> "Artikel":
        """Record a relevance score, transitioning EINGEGANGEN -> BEWERTET.

        Raises:
            UngueltigerZustandsuebergangError: if this Artikel is not
                currently EINGEGANGEN.
        """
        if self.status != ArtikelStatus.EINGEGANGEN:
            raise UngueltigerZustandsuebergangError(
                f"Cannot score an Artikel in status {self.status}; expected EINGEGANGEN."
            )
        return replace(self, status=ArtikelStatus.BEWERTET, relevanz_score=score)

    def verwerfen(self) -> "Artikel":
        """Discard a scored, non-relevant Artikel, transitioning BEWERTET -> VERWORFEN.

        Enforces R1 itself: a caller can never discard an Artikel whose
        score meets the relevance threshold, even by mistake.

        Raises:
            UngueltigerZustandsuebergangError: if this Artikel is not
                BEWERTET, or its score is still relevant (R1).
        """
        if self.status != ArtikelStatus.BEWERTET:
            raise UngueltigerZustandsuebergangError(
                f"Cannot discard an Artikel in status {self.status}; expected BEWERTET."
            )
        if self.relevanz_score is None or self.relevanz_score.ist_relevant():
            raise UngueltigerZustandsuebergangError(
                "Cannot discard an Artikel whose score still meets the relevance threshold (R1)."
            )
        return replace(self, status=ArtikelStatus.VERWORFEN)

