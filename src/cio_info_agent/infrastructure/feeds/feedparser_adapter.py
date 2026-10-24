"""FeedPort implementation backed by the `feedparser` library."""

from __future__ import annotations

import socket
from datetime import datetime, timezone
from time import struct_time

import feedparser

from cio_info_agent.application.ports.feed_port import FeedEintrag, FeedNichtErreichbarError

# feedparser issues a plain blocking network call with no timeout parameter of
# its own; a hanging source would otherwise block ingestion indefinitely,
# defeating FR1's one-source-does-not-block-the-others guarantee. Setting the
# process-global socket default timeout around the call is the documented
# workaround for feedparser specifically (it delegates to urllib, which
# honors this). Restored in `finally` so it never leaks beyond this call.
_FETCH_TIMEOUT_SECONDS = 10


class FeedparserAdapter:
    """Reads feed entries via `feedparser.parse`."""

    def lies_eintraege(self, feed_url: str) -> list[FeedEintrag]:
        """Fetch and parse the feed at `feed_url`.

        Raises:
            FeedNichtErreichbarError: if `feedparser` could not fetch or
                parse the feed at all (an exception during parsing, or the
                `bozo` flag set with zero entries returned — a well-formed
                feed that merely has quirks but still yields entries is not
                treated as unreachable).
        """
        geparst = self._parse_mit_timeout(feed_url)

        if getattr(geparst, "bozo", False) and not geparst.entries:
            bozo_exception = getattr(geparst, "bozo_exception", None)
            raise FeedNichtErreichbarError(
                f"Feed at {feed_url} is malformed and yielded no entries: {bozo_exception}"
            )

        eintraege: list[FeedEintrag] = []
        for entry in geparst.entries:
            # A single malformed entry (e.g. an unparseable publish date)
            # must never crash the whole feed — let alone the whole
            # ingestion run across all five sources (FR1). Skip just that
            # entry instead of letting the exception propagate.
            eintrag = self._zu_feed_eintrag(entry)
            if eintrag is not None:
                eintraege.append(eintrag)
        return eintraege

    @staticmethod
    def _parse_mit_timeout(feed_url: str) -> feedparser.util.FeedParserDict:
        previous_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(_FETCH_TIMEOUT_SECONDS)
        try:
            return feedparser.parse(feed_url)
        except Exception as exc:  # feedparser itself rarely raises, but transport
            # libraries it delegates to can.
            raise FeedNichtErreichbarError(
                f"Failed to fetch or parse feed at {feed_url}: {exc}"
            ) from exc
        finally:
            socket.setdefaulttimeout(previous_timeout)

    @staticmethod
    def _zu_feed_eintrag(entry: object) -> FeedEintrag | None:
        """Convert one raw feedparser entry, or None to skip an unusable one.

        An entry without a link is skipped entirely rather than defaulted to
        an empty string: ArtikelId is derived from (quelle, link), so every
        linkless entry from one source would otherwise collide onto the same
        id and silently drop all but the first as a false duplicate. A link
        is also what FR8's future Deep Dive command needs to reference.
        """
        link = getattr(entry, "link", "") or ""
        if not link:
            return None

        titel = getattr(entry, "title", "")
        veroeffentlicht_struct: struct_time | None = getattr(entry, "published_parsed", None)
        veroeffentlicht_am: datetime | None = None
        if veroeffentlicht_struct is not None:
            try:
                veroeffentlicht_am = datetime(*veroeffentlicht_struct[:6], tzinfo=timezone.utc)
            except (ValueError, TypeError):
                # A malformed date must not crash the entry (or the whole
                # feed) — fall back to "no date", same as a feed that never
                # published one at all.
                veroeffentlicht_am = None
        return FeedEintrag(link=link, titel=titel, veroeffentlicht_am=veroeffentlicht_am)
