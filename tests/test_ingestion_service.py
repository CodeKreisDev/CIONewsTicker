"""Tests for IngestionService: all sources, partial-failure tolerance, dedup."""

from __future__ import annotations

from datetime import datetime, timezone

from cio_info_agent.application.ports.feed_port import FeedEintrag, FeedNichtErreichbarError
from cio_info_agent.application.services.ingestion_service import IngestionService
from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_id import ArtikelId
from cio_info_agent.domain.artikel.quelle import Quelle

ALLE_QUELLEN_URLS = {
    Quelle.CIO_COM: "https://cio.example/feed",
    Quelle.BSI: "https://bsi.example/feed",
    Quelle.HAUFE_IMMOBILIEN: "https://haufe.example/feed",
    Quelle.PROPMODO: "https://propmodo.example/feed",
    Quelle.BITKOM: "https://bitkom.example/feed",
}


class FakeFeedPort:
    """Returns pre-configured entries per feed URL, or raises for configured failures."""

    def __init__(
        self,
        eintraege_je_url: dict[str, list[FeedEintrag]] | None = None,
        fehlerhafte_urls: set[str] | None = None,
    ) -> None:
        self._eintraege_je_url = eintraege_je_url or {}
        self._fehlerhafte_urls = fehlerhafte_urls or set()

    def lies_eintraege(self, feed_url: str) -> list[FeedEintrag]:
        if feed_url in self._fehlerhafte_urls:
            raise FeedNichtErreichbarError(f"simulated failure for {feed_url}")
        return self._eintraege_je_url.get(feed_url, [])


class FakeArtikelRepository:
    """In-memory repository, tracks existence by ArtikelId."""

    def __init__(self) -> None:
        self._gespeicherte: dict[ArtikelId, Artikel] = {}

    def existiert(self, artikel_id: ArtikelId) -> bool:
        return artikel_id in self._gespeicherte

    def speichere(self, artikel: Artikel) -> None:
        self._gespeicherte[artikel.id] = artikel


def test_ingestiere_alle_quellen_queries_all_five_sources() -> None:
    feed_port = FakeFeedPort()
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    # Track which URLs were actually queried.
    queried: list[str] = []
    original = feed_port.lies_eintraege

    def tracking_lies_eintraege(feed_url: str) -> list[FeedEintrag]:
        queried.append(feed_url)
        return original(feed_url)

    feed_port.lies_eintraege = tracking_lies_eintraege  # type: ignore[method-assign]

    service.ingestiere_alle_quellen()

    assert set(queried) == set(ALLE_QUELLEN_URLS.values())


def test_new_entries_are_stored_as_eingegangen() -> None:
    eintrag = FeedEintrag(
        link="https://example.com/new",
        titel="New article",
        veroeffentlicht_am=datetime(2026, 10, 23, tzinfo=timezone.utc),
        beschreibung="A description from the feed.",
    )
    feed_port = FakeFeedPort(eintraege_je_url={ALLE_QUELLEN_URLS[Quelle.CIO_COM]: [eintrag]})
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    ergebnis = service.ingestiere_alle_quellen()

    assert len(ergebnis.neue_artikel) == 1
    assert ergebnis.neue_artikel[0].link == "https://example.com/new"
    assert ergebnis.neue_artikel[0].beschreibung == "A description from the feed."
    assert repository.existiert(
        ArtikelId.von_quelle_und_link(Quelle.CIO_COM, "https://example.com/new")
    )


def test_one_failing_source_does_not_block_the_others() -> None:
    eintrag = FeedEintrag(
        link="https://example.com/ok",
        titel="Still works",
        veroeffentlicht_am=None,
    )
    feed_port = FakeFeedPort(
        eintraege_je_url={ALLE_QUELLEN_URLS[Quelle.PROPMODO]: [eintrag]},
        fehlerhafte_urls={ALLE_QUELLEN_URLS[Quelle.BSI]},
    )
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    ergebnis = service.ingestiere_alle_quellen()

    assert ergebnis.fehlgeschlagene_quellen == [Quelle.BSI]
    assert len(ergebnis.neue_artikel) == 1
    assert ergebnis.neue_artikel[0].link == "https://example.com/ok"


def test_already_known_article_is_not_ingested_again() -> None:
    eintrag = FeedEintrag(
        link="https://example.com/dup",
        titel="Duplicate",
        veroeffentlicht_am=None,
    )
    feed_port = FakeFeedPort(eintraege_je_url={ALLE_QUELLEN_URLS[Quelle.BITKOM]: [eintrag]})
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    erster_lauf = service.ingestiere_alle_quellen()
    zweiter_lauf = service.ingestiere_alle_quellen()

    assert len(erster_lauf.neue_artikel) == 1
    assert len(zweiter_lauf.neue_artikel) == 0


def test_missing_published_date_falls_back_to_now_instead_of_crashing() -> None:
    eintrag = FeedEintrag(
        link="https://example.com/no-date",
        titel="No date",
        veroeffentlicht_am=None,
    )
    feed_port = FakeFeedPort(eintraege_je_url={ALLE_QUELLEN_URLS[Quelle.HAUFE_IMMOBILIEN]: [eintrag]})
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    ergebnis = service.ingestiere_alle_quellen()

    assert len(ergebnis.neue_artikel) == 1
    assert ergebnis.neue_artikel[0].veroeffentlicht_am is not None


def test_entries_without_a_link_are_skipped_not_collided() -> None:
    # Regression test: two distinct entries sharing an empty link must never
    # silently collapse onto the same ArtikelId (only the first stored, the
    # second dropped as a false duplicate). Both are skipped entirely.
    linkless_a = FeedEintrag(link="", titel="First linkless", veroeffentlicht_am=None)
    linkless_b = FeedEintrag(link="", titel="Second linkless", veroeffentlicht_am=None)
    feed_port = FakeFeedPort(
        eintraege_je_url={ALLE_QUELLEN_URLS[Quelle.CIO_COM]: [linkless_a, linkless_b]}
    )
    repository = FakeArtikelRepository()
    service = IngestionService(feed_port, repository, ALLE_QUELLEN_URLS)

    ergebnis = service.ingestiere_alle_quellen()

    assert ergebnis.neue_artikel == []
    assert ergebnis.fehlgeschlagene_quellen == []
