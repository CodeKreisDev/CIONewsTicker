"""Port for persisting and querying Artikel aggregates.

Infrastructure provides the concrete (SQLite) implementation; the application
layer only ever depends on this Protocol (AD-6).
"""

from __future__ import annotations

from typing import Protocol

from cio_info_agent.domain.artikel.artikel import Artikel
from cio_info_agent.domain.artikel.artikel_id import ArtikelId


class ArtikelRepositoryPort(Protocol):
    """Persists and queries Artikel aggregates by their ArtikelId."""

    def existiert(self, artikel_id: ArtikelId) -> bool:
        """Return True if an Artikel with this id is already stored."""
        ...

    def speichere(self, artikel: Artikel) -> None:
        """Persist a newly-ingested Artikel."""
        ...
