"""
Domain errors.

These exceptions are raised by services and other domain-layer code.
They are framework-agnostic and must NOT depend on FastAPI/HTTP.
"""

import typing as tp


class DomainError(Exception):
    """Base class for all domain-level errors."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        meta: dict[str, tp.Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.meta = meta or {}


class BadRequestError(DomainError):
    """The request is invalid in current domain state (maps to HTTP 400)."""


class UnauthorizedError(DomainError):
    """Authentication required/failed (maps to HTTP 401)."""


class ForbiddenError(DomainError):
    """Action is not allowed for current actor (maps to HTTP 403)."""


class NotFoundError(DomainError):
    """Requested entity not found (maps to HTTP 404)."""


class ConflictError(DomainError):
    """Conflict with existing state (maps to HTTP 409)."""


class InternalError(DomainError):
    """Unexpected domain failure (maps to HTTP 500)."""

