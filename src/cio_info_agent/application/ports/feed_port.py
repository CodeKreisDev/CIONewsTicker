"""Port for reading entries from a single RSS feed source.

Infrastructure adapters implement this; the application layer never talks to
feedparser, HTTP, or any other transport detail directly (AD-6).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class FeedEintrag:
    """A single raw entry read from a feed, before it becomes an Artikel."""

    link: str
    titel: str
    veroeffentlicht_am: datetime | None


class FeedNichtErreichbarError(RuntimeError):
    """Raised when a single feed source could not be read.

    Caught per-source by the orchestrating service (IngestionService), so one
    unreachable source never blocks the remaining sources (FR1).
    """


class FeedPort(Protocol):
    """Reads entries from one RSS feed source."""

    def lies_eintraege(self, feed_url: str) -> list[FeedEintrag]:
        """Fetch and parse all entries currently published at `feed_url`.

        Raises:
            FeedNichtErreichbarError: if the source cannot be fetched or
                parsed.
        """
        ...
