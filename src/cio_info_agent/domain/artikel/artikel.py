"""Artikel aggregate root.

An Artikel is identified by its ArtikelId (derived from Quelle + Link) and
carries its own lifecycle state. This story only ever produces an Artikel in
the EINGEGANGEN state via the `eingegangen` factory; later stories transition
it onward through scoring, filtering, and synthesis.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.artikel_status import ArtikelStatus
from cio_info_agent.domain.artikel.quelle import Quelle


@dataclass(frozen=True)
class Artikel:
    """Aggregate root for a single ingested news article.

    Frozen by design: an Artikel's recorded facts (id, source, link, title,
    timestamps) never change after ingestion. State transitions in later
    stories are modeled as producing a new, updated Artikel instance (e.g.
    via a `bewertet(...)` factory), not by mutating this one in place.
    """

    id: ArtikelId
    quelle: Quelle
    link: str
    titel: str
    veroeffentlicht_am: datetime
    eingegangen_am: datetime
    status: ArtikelStatus

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
        )
