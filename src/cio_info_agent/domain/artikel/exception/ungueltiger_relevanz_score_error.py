"""Raised when a RelevanzScore is constructed outside the valid 1-10 range."""

from __future__ import annotations

from cio_info_agent.domain.exception.domain_exception import DomainException


class UngueltigerRelevanzScoreError(DomainException):
    """A relevance score outside the valid 1-10 range was supplied."""
