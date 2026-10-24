"""Port for scoring an Artikel's relevance via an LLM.

Infrastructure provides the concrete provider adapter; the application layer
only ever depends on this Protocol (AD-6), so the LLM provider is swappable
without touching domain or application code.
"""

from __future__ import annotations

from typing import Protocol


class LLMNichtErreichbarError(RuntimeError):
    """Raised when the LLM provider could not be reached (network/API error).

    Caught per-Artikel by the orchestrating service (ScoringService), so one
    failed scoring attempt never blocks scoring of the remaining Artikel.
    """


class LLMAntwortUngueltigError(RuntimeError):
    """Raised when the LLM responded, but not with a parseable 1-10 score.

    Handled the same way as LLMNichtErreichbarError by the caller: the
    Artikel in question is simply not scored this run, nothing crashes.
    """


class LLMPort(Protocol):
    """Scores a single Artikel's relevance for the CIO persona."""

    def bewerte_relevanz(self, titel: str, beschreibung: str) -> int:
        """Return a relevance score from 1 (irrelevant) to 10 (critical).

        Raises:
            LLMNichtErreichbarError: if the provider could not be reached.
            LLMAntwortUngueltigError: if the response could not be parsed
                into a valid 1-10 integer.
        """
        ...
