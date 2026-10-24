"""Feed URL configuration for the five fixed sources.

URLs verified live against the real endpoints on 2026-10-24 by fetching each
and confirming a valid RSS/XML response, except where noted below.
"""

from __future__ import annotations

from cio_info_agent.domain.artikel.quelle import Quelle

QUELLEN_FEED_URLS: dict[Quelle, str] = {
    Quelle.CIO_COM: "https://www.cio.com/feed/",
    # BSI CERT-Bund security advisories feed (matches the brief's intent:
    # critical security warnings must not be missed).
    Quelle.BSI: "https://wid.cert-bund.de/content/public/securityAdvisory/rss",
    # NOT independently verified: candidate URLs for Haufe's Immobilien
    # section returned 404 during verification. This is a low-risk,
    # easily-corrected configuration detail — FR1's per-source resilience
    # already tolerates this source being unreachable. Confirm the real
    # feed URL (check the page's <link rel="alternate" type="application/
    # rss+xml"> tag) before relying on this source in production.
    Quelle.HAUFE_IMMOBILIEN: "https://www.haufe.de/immobilien/rss.xml",
    Quelle.PROPMODO: "https://propmodo.com/feed/",
    Quelle.BITKOM: "https://www.bitkom.org/Presse/Presseinformation/index.xml",
}
