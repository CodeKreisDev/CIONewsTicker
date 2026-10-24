"""The five fixed public RSS sources this system ingests from.

Modeled as a closed enum rather than a free value object: the set of sources
is a product decision (see the Product Brief), not something a developer can
extend ad-hoc. The feed URL itself is an infrastructure access detail and
lives in `infrastructure/feeds/quellen_konfiguration.py`, never here (AD-1).
"""

from __future__ import annotations

from enum import Enum


class Quelle(str, Enum):
    """One of the five fixed, publicly accessible RSS sources."""

    CIO_COM = "cio_com"
    BSI = "bsi"
    HAUFE_IMMOBILIEN = "haufe_immobilien"
    PROPMODO = "propmodo"
    BITKOM = "bitkom"
