"""Lifecycle states of an Artikel, as validated in the domain model.

Only EINGEGANGEN is produced by this story's ingestion logic. The remaining
states are defined here because they are part of one validated state machine
(domain-discovery-cio-info-agent.md §7.2) and later stories (scoring,
synthesis) transition an Artikel through them — defining the enum piecemeal
across stories would fragment a single state machine across files.
"""

from __future__ import annotations

from enum import Enum


class ArtikelStatus(str, Enum):
    """A state in the validated Artikel lifecycle."""

    EINGEGANGEN = "eingegangen"
    BEWERTET = "bewertet"
    VERWORFEN = "verworfen"
    QUALIFIZIERT_NICHT_AUSGEWAEHLT = "qualifiziert_nicht_ausgewaehlt"
    IM_BRIEFING = "im_briefing"
