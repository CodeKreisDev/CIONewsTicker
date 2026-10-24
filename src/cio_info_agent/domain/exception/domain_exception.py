"""Shared base for domain exceptions (ddd-principles.md convention).

Only cross-cutting exceptions live here. Aggregate-specific exceptions live
under that aggregate's own `exception/` package (e.g.
`domain/artikel/exception/`), per the project's DDD structural rules.
"""

from __future__ import annotations


class DomainException(Exception):
    """Base for every exception raised from the domain layer.

    Never raise a generic exception (ValueError, RuntimeError, ...) from
    domain logic for a business-rule violation — always a specific
    subclass of this, so callers can distinguish domain errors from
    programming errors. (Artikel's timezone-awareness check is a
    precondition violation, not a business rule, so it intentionally stays a
    plain ValueError — only aggregate-state and business-rule violations go
    through this hierarchy.)
    """
