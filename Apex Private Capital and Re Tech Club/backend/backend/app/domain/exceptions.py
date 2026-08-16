"""Domain-level exceptions.

These carry business meaning (e.g. "tenant not found", "asset already
retired") and are translated into HTTP responses at the API layer -- the
domain layer itself never knows what an HTTP status code is.
"""

from __future__ import annotations


class DomainError(Exception):
    """Base class for all domain-level errors."""


class EntityNotFoundError(DomainError):
    """Raised when a requested entity does not exist."""


class TenantNotFoundError(EntityNotFoundError):
    """Raised when a tenant code does not resolve to a known, active tenant."""


class TenantAccessDeniedError(DomainError):
    """Raised when an actor is not a member of the tenant they are requesting."""
