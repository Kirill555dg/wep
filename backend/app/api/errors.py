"""
API-level error handling.

Strategy:
- Services return optional results (e.g. ``None`` when an entity is missing)
  or raise no custom exceptions. API handlers translate these results into
  ``HTTPException`` with explicit status codes and a structured payload.
- This module wraps every HTTP error into a single response envelope:
  ``{"error": {"code", "message", "meta"}, "request_id": ...}``.
- Unhandled exceptions are reported as ``500 Internal Server Error`` and
  indicate a bug on the server side.
"""

import logging
import typing as tp

import fastapi
import fastapi.exceptions as fastapi_exceptions
import fastapi.responses as fastapi_responses
import sqlalchemy.exc as sa_exc
import starlette.exceptions as starlette_exceptions
import starlette.status as http_status

from app.core import config as core_config
from app.core import request_context as request_context


logger = logging.getLogger("app.api.errors")


def _request_id() -> str:
    return request_context.get_request_id()


def build_error_content(
    *,
    code: str,
    message: str,
    meta: dict[str, tp.Any] | None = None,
    request_id: str | None = None,
) -> dict[str, tp.Any]:
    """Build a unified error envelope used by every error response."""

    meta_payload: dict[str, tp.Any] = meta or {}
    payload: dict[str, tp.Any] = {
        "error": {
            "code": code,
            "message": message,
            "meta": meta_payload,
        },
        "request_id": request_id or _request_id(),
    }
    return payload


def _default_code_for_status(status_code: int) -> str:
    if status_code == http_status.HTTP_400_BAD_REQUEST:
        return "bad_request"
    if status_code == http_status.HTTP_401_UNAUTHORIZED:
        return "unauthorized"
    if status_code == http_status.HTTP_403_FORBIDDEN:
        return "forbidden"
    if status_code == http_status.HTTP_404_NOT_FOUND:
        return "not_found"
    if status_code == http_status.HTTP_409_CONFLICT:
        return "conflict"
    if status_code == http_status.HTTP_422_UNPROCESSABLE_ENTITY:
        return "validation_error"
    if status_code >= 500:
        return "internal_error"
    return "http_error"


def _http_exception_content(exc: starlette_exceptions.HTTPException) -> dict[str, tp.Any]:
    """Convert ``HTTPException.detail`` (string or dict) into the envelope."""

    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code") or _default_code_for_status(exc.status_code))
        message = str(detail.get("message") or detail.get("detail") or "Request failed")
        meta = detail.get("meta")
        return build_error_content(
            code=code,
            message=message,
            meta=tp.cast(dict[str, tp.Any] | None, meta),
        )

    message = str(detail) if detail is not None else "Request failed"
    return build_error_content(
        code=_default_code_for_status(exc.status_code),
        message=message,
    )


def _extract_sqlstate(exc: sa_exc.DBAPIError) -> str:
    """
    Extract PostgreSQL SQLSTATE code from an asyncpg-wrapped SQLAlchemy error.

    asyncpg stores the original error as a chain:
      sa_exc.DBAPIError
        .orig  → asyncpg dialect adapter
          .__cause__  → asyncpg.exceptions.*  (has .sqlstate)

    Falls back to the adapter itself if the cause is missing.
    """
    orig = exc.orig
    for err in filter(None, [getattr(orig, "__cause__", None), orig]):
        code = getattr(err, "sqlstate", None)
        if code:
            return str(code)
    return ""


def _is_client_fault(sqlstate: str) -> bool:
    """
    Return True when the SQLSTATE indicates bad input data (client's fault).

    PostgreSQL SQLSTATE families that mean "the data you sent is invalid":
      22xxx  Data Exception (null bytes, encoding errors, overflow, etc.)
      23xxx  Integrity Constraint Violation (duplicate key, FK violation, etc.)

    Everything else (08xxx connection, 57xxx operator intervention, 42xxx
    syntax error, …) is an infrastructure or server-side problem.
    """
    return sqlstate[:2] in ("22", "23")


def register_exception_handlers(app: fastapi.FastAPI) -> None:
    """Install the three exception handlers used by the application."""

    @app.exception_handler(starlette_exceptions.HTTPException)
    async def http_exception_handler(
        request: fastapi.Request,  # noqa: ARG001
        exc: starlette_exceptions.HTTPException,
    ) -> fastapi_responses.JSONResponse:
        return fastapi_responses.JSONResponse(
            status_code=exc.status_code,
            content=_http_exception_content(exc),
            headers=exc.headers,
        )

    @app.exception_handler(fastapi_exceptions.RequestValidationError)
    async def request_validation_handler(
        request: fastapi.Request,
        exc: fastapi_exceptions.RequestValidationError,
    ) -> fastapi_responses.JSONResponse:
        errors = exc.errors()
        body = exc.body if hasattr(exc, "body") else None

        meta: dict[str, tp.Any] = {"errors": errors}
        if core_config.settings.DEBUG:
            meta["body"] = body

        logger.warning(
            "request_validation_error",
            extra={"path": request.url.path, "errors": errors},
        )

        return fastapi_responses.JSONResponse(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_content(
                code="validation_error",
                message="Validation error",
                meta=meta,
            ),
        )

    @app.exception_handler(sa_exc.DBAPIError)
    async def db_api_error_handler(
        request: fastapi.Request,
        exc: sa_exc.DBAPIError,
    ) -> fastapi_responses.JSONResponse:
        sqlstate = _extract_sqlstate(exc)
        if _is_client_fault(sqlstate):
            logger.warning("db_client_error", extra={"path": request.url.path, "sqlstate": sqlstate})
            return fastapi_responses.JSONResponse(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=build_error_content(code="invalid_input", message="Input value rejected by the database"),
            )
        logger.exception("db_infra_error", extra={"path": request.url.path, "sqlstate": sqlstate})
        meta: dict[str, tp.Any] | None = None
        if core_config.settings.DEBUG:
            meta = {"exception": type(exc).__name__, "sqlstate": sqlstate, "detail": str(exc.orig)}
        return fastapi_responses.JSONResponse(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_content(code="internal_error", message="Internal server error", meta=meta),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: fastapi.Request,  # noqa: ARG001
        exc: Exception,
    ) -> fastapi_responses.JSONResponse:
        logger.exception("unhandled_exception")

        # Hide internals in production; expose them in DEBUG to ease diagnosis.
        meta: dict[str, tp.Any] | None = None
        if core_config.settings.DEBUG:
            meta = {"exception": type(exc).__name__, "detail": str(exc)}

        return fastapi_responses.JSONResponse(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=build_error_content(
                code="internal_error",
                message="Internal server error",
                meta=meta,
            ),
        )
