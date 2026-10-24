"""Orchestrates ingestion of new Artikel across all five configured sources.

Resilience (FR1) and deduplication (FR2) are deliberately visible here, in the
application layer, rather than hidden inside an adapter — this is the use
case a future builder reads to understand "what happens when a source fails"
and "how a duplicate is detected", without having to trace into
infrastructure code.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from cio_info_agent.application.ports.artikel_repository_port import (
    ArtikelRepositoryPort,
)
from cio_info_agent.application.ports.feed_port import FeedNichtErreichbarError, FeedPort
from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.quelle import Quelle


@dataclass(frozen=True)
class IngestionErgebnis:
    """Outcome of one ingestion run across all configured sources."""

    neue_artikel: list[Artikel] = field(default_factory=list)
    fehlgeschlagene_quellen: list[Quelle] = field(default_factory=list)


class IngestionService:
    """Reads all configured sources and stores newly-seen Artikel."""

    def __init__(
        self,
        feed_port: FeedPort,
        repository: ArtikelRepositoryPort,
        quellen_feed_urls: dict[Quelle, str],
    ) -> None:
        self._feed_port = feed_port
        self._repository = repository
        self._quellen_feed_urls = quellen_feed_urls

    def ingestiere_alle_quellen(self) -> IngestionErgebnis:
        """Ingest new Artikel from every configured source.

        A source that cannot be read is recorded in
        `IngestionErgebnis.fehlgeschlagene_quellen` and does not prevent the
        remaining sources from being processed (FR1).
        """
        neue_artikel: list[Artikel] = []
        fehlgeschlagene_quellen: list[Quelle] = []

        for quelle, feed_url in self._quellen_feed_urls.items():
            try:
                eintraege = self._feed_port.lies_eintraege(feed_url)
            except FeedNichtErreichbarError:
                fehlgeschlagene_quellen.append(quelle)
                continue

            for eintrag in eintraege:
                if not eintrag.link:
                    # Defense in depth: an Artikel's identity is derived from
                    # (quelle, link) — an entry without a link can never be
                    # safely deduplicated (every such entry from one source
                    # would collide onto the same ArtikelId) and has nothing
                    # for FR8's future Deep Dive to link back to. Any FeedPort
                    # implementation, not only FeedparserAdapter, is guarded
                    # here.
                    continue

                artikel_id = ArtikelId.von_quelle_und_link(quelle, eintrag.link)
                if self._repository.existiert(artikel_id):
                    continue

                jetzt = datetime.now(timezone.utc)
                artikel = Artikel.eingegangen(
                    quelle=quelle,
                    link=eintrag.link,
                    titel=eintrag.titel,
                    veroeffentlicht_am=eintrag.veroeffentlicht_am or jetzt,
                    eingegangen_am=jetzt,
                )
                self._repository.speichere(artikel)
                neue_artikel.append(artikel)

        return IngestionErgebnis(
            neue_artikel=neue_artikel,
            fehlgeschlagene_quellen=fehlgeschlagene_quellen,
        )
