"""Tests for FeedparserAdapter against embedded RSS fixtures (no network access)."""

from __future__ import annotations

from datetime import timezone

import pytest

from cio_info_agent.application.ports.feed_port import FeedNichtErreichbarError
from cio_info_agent.infrastructure.feeds.feedparser_adapter import FeedparserAdapter

_VALID_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fixture Feed</title>
    <item>
      <title>Article One</title>
      <link>https://example.com/article-one</link>
      <description>A short summary of article one.</description>
      <pubDate>Fri, 23 Oct 2026 10:00:00 GMT</pubDate>
    </item>
    <item>
      <title>Article Without Date</title>
      <link>https://example.com/article-no-date</link>
    </item>
  </channel>
</rss>
"""

_MISSING_LINK_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Fixture Feed</title>
    <item>
      <title>Has A Link</title>
      <link>https://example.com/has-link</link>
    </item>
    <item>
      <title>No Link At All</title>
    </item>
  </channel>
</rss>
"""

# A raw, unescaped "&" in element text is invalid XML; feedparser's lenient
# parser still recovers the entries but sets `bozo=True`. This fixture lets
# the "malformed but still yields entries" path be tested without a live
# network fetch.
_BOZO_BUT_PARSEABLE_FEED_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Bozo Feed</title>
    <item>
      <title>Bozo & Co</title>
      <link>https://example.com/bozo</link>
    </item>
  </channel>
</rss>
"""

_GARBAGE_CONTENT = "this is not a feed at all, just plain garbage text {{{"


def test_lies_eintraege_parses_valid_feed_entries() -> None:
    adapter = FeedparserAdapter()

    eintraege = adapter.lies_eintraege(_VALID_FEED_XML)

    assert len(eintraege) == 2
    assert eintraege[0].link == "https://example.com/article-one"
    assert eintraege[0].titel == "Article One"
    assert eintraege[0].veroeffentlicht_am is not None
    assert eintraege[0].veroeffentlicht_am.tzinfo is timezone.utc


def test_lies_eintraege_handles_missing_published_date() -> None:
    adapter = FeedparserAdapter()

    eintraege = adapter.lies_eintraege(_VALID_FEED_XML)

    entry_without_date = next(e for e in eintraege if e.link == "https://example.com/article-no-date")
    assert entry_without_date.veroeffentlicht_am is None


def test_lies_eintraege_extracts_description_into_beschreibung() -> None:
    adapter = FeedparserAdapter()

    eintraege = adapter.lies_eintraege(_VALID_FEED_XML)

    entry_with_description = next(e for e in eintraege if e.link == "https://example.com/article-one")
    assert entry_with_description.beschreibung == "A short summary of article one."


def test_lies_eintraege_skips_entries_without_a_link() -> None:
    adapter = FeedparserAdapter()

    eintraege = adapter.lies_eintraege(_MISSING_LINK_FEED_XML)

    assert len(eintraege) == 1
    assert eintraege[0].link == "https://example.com/has-link"


def test_lies_eintraege_does_not_raise_when_bozo_but_entries_present() -> None:
    adapter = FeedparserAdapter()

    eintraege = adapter.lies_eintraege(_BOZO_BUT_PARSEABLE_FEED_XML)

    assert len(eintraege) == 1
    assert eintraege[0].link == "https://example.com/bozo"


def test_lies_eintraege_raises_on_unparseable_content() -> None:
    adapter = FeedparserAdapter()

    with pytest.raises(FeedNichtErreichbarError):
        adapter.lies_eintraege(_GARBAGE_CONTENT)
