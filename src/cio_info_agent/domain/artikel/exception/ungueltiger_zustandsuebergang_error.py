"""Raised when an Artikel state transition is attempted that violates its
lifecycle or a business rule tied to that lifecycle.
"""

from __future__ import annotations

from cio_info_agent.domain.exception.domain_exception import DomainException


class UngueltigerZustandsuebergangError(DomainException):
    """An Artikel state transition was attempted that is not currently allowed."""
