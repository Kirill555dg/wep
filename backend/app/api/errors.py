"""
API-level error mapping.

Converts domain errors (raised by services) into HTTP responses.
"""

import typing as tp

import logging

import fastapi
import fastapi.exceptions as fastapi_exceptions
import fastapi.responses as fastapi_responses
import starlette.exceptions as starlette_exceptions
import starlette.status as http_status

from app.core import config as core_config
from app.core import request_context as request_context
from app.domain import errors as domain_errors


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


def _status_code(exc: domain_errors.DomainError) -> int:
    if isinstance(exc, domain_errors.BadRequestError):
        return http_status.HTTP_400_BAD_REQUEST
    if isinstance(exc, domain_errors.UnauthorizedError):
        return http_status.HTTP_401_UNAUTHORIZED
    if isinstance(exc, domain_errors.ForbiddenError):
        return http_status.HTTP_403_FORBIDDEN
    if isinstance(exc, domain_errors.NotFoundError):
        return http_status.HTTP_404_NOT_FOUND
    if isinstance(exc, domain_errors.ConflictError):
        return http_status.HTTP_409_CONFLICT
    if isinstance(exc, domain_errors.InternalError):
        return http_status.HTTP_500_INTERNAL_SERVER_ERROR
    return http_status.HTTP_400_BAD_REQUEST


def _domain_code(exc: domain_errors.DomainError) -> str:
    if exc.code:
        return exc.code
    if isinstance(exc, domain_errors.BadRequestError):
        return "bad_request"
    if isinstance(exc, domain_errors.UnauthorizedError):
        return "unauthorized"
    if isinstance(exc, domain_errors.ForbiddenError):
        return "forbidden"
    if isinstance(exc, domain_errors.NotFoundError):
        return "not_found"
    if isinstance(exc, domain_errors.ConflictError):
        return "conflict"
    if isinstance(exc, domain_errors.InternalError):
        return "internal_error"
    return "domain_error"


def _http_exception_content(exc: starlette_exceptions.HTTPException) -> dict[str, tp.Any]:
    detail = exc.detail
    if isinstance(detail, dict):
        code = str(detail.get("code") or "http_error")
        message = str(detail.get("message") or detail.get("detail") or "Request failed")
        meta = detail.get("meta")
        return build_error_content(code=code, message=message, meta=tp.cast(dict[str, tp.Any] | None, meta))

    message = str(detail) if detail is not None else "Request failed"
    default_code = "http_error"
    if exc.status_code == http_status.HTTP_401_UNAUTHORIZED:
        default_code = "unauthorized"
    elif exc.status_code == http_status.HTTP_403_FORBIDDEN:
        default_code = "forbidden"
    elif exc.status_code == http_status.HTTP_404_NOT_FOUND:
        default_code = "not_found"
    return build_error_content(code=default_code, message=message)


def register_exception_handlers(app: fastapi.FastAPI) -> None:
    @app.exception_handler(domain_errors.DomainError)
    async def domain_error_handler(
        request: fastapi.Request,  # noqa: ARG001
        exc: domain_errors.DomainError,
    ) -> fastapi_responses.JSONResponse:
        payload = build_error_content(
            code=_domain_code(exc),
            message=exc.message,
            meta=exc.meta or None,
        )
        return fastapi_responses.JSONResponse(
            status_code=_status_code(exc),
            content=payload,
        )

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

        logger.warning("request_validation_error", extra={"path": request.url.path, "errors": errors})

        return fastapi_responses.JSONResponse(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_content(code="validation_error", message="Validation error", meta=meta),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: fastapi.Request,  # noqa: ARG001
        exc: Exception,
    ) -> fastapi_responses.JSONResponse:
        logger.exception("unhandled_exception")

        # Keep response stable and non-leaky; details can be exposed only in DEBUG.
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

