"""Identity of an Artikel, derived deterministically from its source and link.

Deterministic derivation is the mechanism behind FR2 (no duplicate reporting
within the dedup window): the same (Quelle, Link) pair always yields the same
ArtikelId, so existence-checking the repository by ID is sufficient to detect
a previously-seen article without a separate dedup index.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from cio_info_agent.domain.artikel.quelle import Quelle


@dataclass(frozen=True)
class ArtikelId:
    """Deterministic identity of an Artikel, derived from (Quelle, Link)."""

    wert: str

    @classmethod
    def von_quelle_und_link(cls, quelle: Quelle, link: str) -> "ArtikelId":
        """Derive the identity from a source and a link.

        The same (quelle, link) pair always produces the same ArtikelId,
        regardless of when or how many times it is computed.
        """
        digest_input = f"{quelle.value}:{link}".encode("utf-8")
        digest = hashlib.sha256(digest_input).hexdigest()
        return cls(wert=digest)
