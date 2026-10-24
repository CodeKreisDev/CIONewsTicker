"""Relevance score value object.

The 1-10 scale and the relevance threshold (R1: a score below 7 means
not-relevant) are both domain knowledge about what a score *means* — they
belong on this value object, not as a magic number scattered across the
application layer that happens to call it.
"""

from __future__ import annotations

from dataclasses import dataclass

from cio_info_agent.domain.artikel.exception.ungueltiger_relevanz_score_error import (
    UngueltigerRelevanzScoreError,
)

_MINIMUM = 1
_MAXIMUM = 10
_SCHWELLENWERT = 7


@dataclass(frozen=True)
class RelevanzScore:
    """A validated relevance score on the fixed 1-10 scale."""

    wert: int

    def __post_init__(self) -> None:
        if not (_MINIMUM <= self.wert <= _MAXIMUM):
            raise UngueltigerRelevanzScoreError(
                f"RelevanzScore must be between {_MINIMUM} and {_MAXIMUM}, got {self.wert}."
            )

    def ist_relevant(self) -> bool:
        """Return True if this score meets the relevance threshold (R1)."""
        return self.wert >= _SCHWELLENWERT
