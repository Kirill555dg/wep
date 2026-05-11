"""
WebSocket authentication helpers.

Failures are signalled via :class:`ServiceError` from the services layer.
The WebSocket entry point catches it and translates to a closing frame with
a structured payload.
"""

import logging

import fastapi
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import security as core_security
from app.models import users as user_models
from app.repositories import user as user_repository
from app.services import exceptions as service_exceptions


logger = logging.getLogger("app.realtime.auth")


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.strip().split()
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1]


def extract_websocket_token(websocket: fastapi.WebSocket) -> str | None:
    token = websocket.query_params.get("token")
    if token:
        return str(token)
    return extract_bearer_token(websocket.headers.get("authorization"))


async def require_current_user(
    websocket: fastapi.WebSocket,
    db: sa_asyncio.AsyncSession,
) -> user_models.User:
    token = extract_websocket_token(websocket)
    if not token:
        raise service_exceptions.ServiceError("Missing token", code="unauthorized")

    payload = core_security.decode_access_token(token)
    if not payload:
        raise service_exceptions.ServiceError(
            "Invalid or expired token", code="unauthorized",
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise service_exceptions.ServiceError(
            "Invalid token payload", code="unauthorized",
        )

    try:
        user_id = int(user_id_str)
    except Exception:
        raise service_exceptions.ServiceError(
            "Invalid user ID in token", code="unauthorized",
        )

    repo = user_repository.UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise service_exceptions.ServiceError("User not found", code="not_found")
    if not user.is_active:
        raise service_exceptions.ServiceError(
            "User account is inactive", code="forbidden",
        )

    token_role = payload.get("role")
    if token_role is None:
        raise service_exceptions.ServiceError(
            "Token missing role", code="token_missing_role",
        )
    if str(token_role) != str(user.role):
        raise service_exceptions.ServiceError(
            "Role changed, please re-authenticate", code="role_changed",
        )

    logger.debug("ws_user_authenticated", extra={"user_id": user.id})
    return user
