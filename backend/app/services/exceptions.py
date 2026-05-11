"""
Service-layer exceptions.

A single :class:`ServiceError` is raised by service methods that perform
multi-step orchestration whose failure cannot be expressed by a ``None``
return value. API route handlers are expected to catch ``ServiceError``
explicitly and translate it to an HTTP response.

Lookup-style methods (``get_*_by_id`` and similar) return ``None`` instead of
raising ``ServiceError``.
"""

import typing as tp


class ServiceError(Exception):
    """Signal a domain-level failure with a machine-readable code.

    The status code of the HTTP response is decided by the route handler.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str,
        meta: dict[str, tp.Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.meta = meta or {}

    def __str__(self) -> str:  # pragma: no cover - debug aid
        return f"ServiceError(code={self.code!r}, message={self.message!r})"
