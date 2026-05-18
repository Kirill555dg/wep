import dataclasses as dc

import fastapi
from fastapi import security as fastapi_security
from fastapi import status as http_status
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import security as core_security
from app.db import session as db_session
from app.models import users as user_models
from app.repositories import user as user_repo
from app.services import auth as auth_service

security = fastapi_security.HTTPBearer()


@dc.dataclass(frozen=True, slots=True)
class TokenContext:
    user_id: int


def get_current_user_id(
    credentials: fastapi_security.HTTPAuthorizationCredentials = fastapi.Depends(security),
) -> TokenContext:
    token = credentials.credentials
    payload = core_security.decode_access_token(token)

    if not payload:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return TokenContext(user_id=int(user_id))
    except ValueError:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: TokenContext = fastapi.Depends(get_current_user_id),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_models.User:
    user_repository = user_repo.UserRepository(db)
    user = await user_repository.get_by_id(token.user_id)

    if not user:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.is_active:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user


async def get_current_user_optional(
    credentials: fastapi_security.HTTPAuthorizationCredentials | None = fastapi.Depends(fastapi_security.HTTPBearer(auto_error=False)),
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> user_models.User | None:
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = core_security.decode_access_token(token)
    
    if not payload:
        return None
        
    user_id: str | None = payload.get("sub")
    if not user_id:
        return None
    
    try:
        int_user_id = int(user_id)
    except ValueError:
        return None
        
    user_repository = user_repo.UserRepository(db)
    user = await user_repository.get_by_id(int_user_id)
    
    if not user or not user.is_active:
        return None
        
    return user


def get_auth_service(
    db: sa_asyncio.AsyncSession = fastapi.Depends(db_session.get_db),
) -> auth_service.AuthService:
    return auth_service.AuthService(db)
