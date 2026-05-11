"""
HTTP error factories used by API route handlers.

Route handlers raise these exceptions when service-layer code returns an
empty/invalid result. Keeping ``detail`` structured (``{"code", "message",
"meta"}``) lets the unified error envelope in :mod:`app.api.errors` propagate
machine-readable codes to clients without exposing internal exception types.
"""

import typing as tp

import fastapi
import starlette.status as http_status

from app.services import exceptions as service_exceptions


def _http_exc(
    status_code: int,
    *,
    code: str,
    message: str,
    meta: dict[str, tp.Any] | None = None,
    headers: dict[str, str] | None = None,
) -> fastapi.HTTPException:
    detail: dict[str, tp.Any] = {"code": code, "message": message}
    if meta is not None:
        detail["meta"] = meta
    return fastapi.HTTPException(
        status_code=status_code,
        detail=detail,
        headers=headers,
    )


def bad_request(
    message: str,
    *,
    code: str = "bad_request",
    meta: dict[str, tp.Any] | None = None,
) -> fastapi.HTTPException:
    return _http_exc(http_status.HTTP_400_BAD_REQUEST, code=code, message=message, meta=meta)


def unauthorized(
    message: str = "Unauthorized",
    *,
    code: str = "unauthorized",
    meta: dict[str, tp.Any] | None = None,
) -> fastapi.HTTPException:
    return _http_exc(
        http_status.HTTP_401_UNAUTHORIZED,
        code=code,
        message=message,
        meta=meta,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(
    message: str = "Forbidden",
    *,
    code: str = "forbidden",
    meta: dict[str, tp.Any] | None = None,
) -> fastapi.HTTPException:
    return _http_exc(http_status.HTTP_403_FORBIDDEN, code=code, message=message, meta=meta)


def not_found(
    message: str = "Not found",
    *,
    code: str = "not_found",
    meta: dict[str, tp.Any] | None = None,
) -> fastapi.HTTPException:
    return _http_exc(http_status.HTTP_404_NOT_FOUND, code=code, message=message, meta=meta)


def conflict(
    message: str,
    *,
    code: str = "conflict",
    meta: dict[str, tp.Any] | None = None,
) -> fastapi.HTTPException:
    return _http_exc(http_status.HTTP_409_CONFLICT, code=code, message=message, meta=meta)


def from_service_error(
    exc: service_exceptions.ServiceError,
    status_code: int,
) -> fastapi.HTTPException:
    """Translate a :class:`ServiceError` into an explicit ``HTTPException``.

    The status code is chosen by the route handler, which knows the semantic
    meaning of each error code. This avoids any global mapping table that
    would couple HTTP semantics to the services layer.
    """

    headers = (
        {"WWW-Authenticate": "Bearer"}
        if status_code == http_status.HTTP_401_UNAUTHORIZED
        else None
    )
    return _http_exc(
        status_code,
        code=exc.code,
        message=exc.message,
        meta=exc.meta or None,
        headers=headers,
    )
