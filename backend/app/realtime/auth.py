"""
WebSocket authentication helpers.
"""

import logging

import fastapi
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import security as core_security
from app.domain import errors as domain_errors
from app.models import users as user_models
from app.repositories import user as user_repository


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
        raise domain_errors.UnauthorizedError("Missing token")

    payload = core_security.decode_access_token(token)
    if not payload:
        raise domain_errors.UnauthorizedError("Invalid or expired token")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise domain_errors.UnauthorizedError("Invalid token payload")

    try:
        user_id = int(user_id_str)
    except Exception:
        raise domain_errors.UnauthorizedError("Invalid user ID in token")

    repo = user_repository.UserRepository(db)
    user = await repo.get_by_id(user_id)
    if not user:
        raise domain_errors.NotFoundError("User not found")
    if not user.is_active:
        raise domain_errors.ForbiddenError("User account is inactive")

    token_role = payload.get("role")
    if token_role is None:
        raise domain_errors.UnauthorizedError("Token missing role", code="token_missing_role")
    if str(token_role) != str(user.role):
        raise domain_errors.UnauthorizedError(
            "Role changed, please re-authenticate",
            code="role_changed",
        )

    logger.debug("ws_user_authenticated", extra={"user_id": user.id})
    return user

