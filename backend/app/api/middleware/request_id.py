"""
Request ID middleware.

- Reads request id from `X-Request-ID` header (if provided) or generates a new one.
- Stores it in ContextVar so it is available for logging.
- Returns it back in response header.
"""

import logging
import time
import uuid

import fastapi
import starlette.middleware.base as starlette_base
import starlette.types as starlette_types

from app.core import request_context as request_context


logger = logging.getLogger("app.request")


class RequestIdMiddleware(starlette_base.BaseHTTPMiddleware):
    def __init__(self, app: starlette_types.ASGIApp, *, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self._header_name = header_name

    async def dispatch(
        self,
        request: fastapi.Request,
        call_next: starlette_base.RequestResponseEndpoint,
    ) -> fastapi.Response:
        request_id = request.headers.get(self._header_name) or uuid.uuid4().hex
        token = request_context.request_id_var.set(request_id)
        start = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            duration_ms = (time.perf_counter() - start) * 1000.0
            logger.exception(
                "request_failed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                },
            )
            request_context.request_id_var.reset(token)
            raise

        response.headers[self._header_name] = request_id

        duration_ms = (time.perf_counter() - start) * 1000.0
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": round(duration_ms, 2),
            },
        )

        request_context.request_id_var.reset(token)
        return response

