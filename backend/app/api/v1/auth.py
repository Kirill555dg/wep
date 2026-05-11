"""
Authentication endpoints.
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.models import users as user_models
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module
from app.services import exceptions as service_exceptions

router = fastapi.APIRouter()


@router.post(
    "/register",
    response_model=user_schemas.UserResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def register(
    user_data: user_schemas.UserCreate,
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.UserResponse:
    """Register new user (student or teacher)."""
    try:
        return await auth_service.register_user(user_data)
    except service_exceptions.ServiceError as exc:
        if exc.code == "email_taken":
            raise http_errors.bad_request(exc.message, code=exc.code)
        raise


@router.post("/login", response_model=user_schemas.TokenResponse)
async def login(
    credentials: user_schemas.LoginRequest,
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.TokenResponse:
    """Authenticate user and return JWT token."""
    try:
        token = await auth_service.authenticate(credentials)
    except service_exceptions.ServiceError as exc:
        if exc.code == "inactive_user":
            raise http_errors.forbidden(exc.message, code=exc.code)
        raise
    if token is None:
        raise http_errors.unauthorized("Invalid username/email or password")
    return token


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_profile(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> user_schemas.UserResponse:
    """Return the authenticated user's profile."""
    return user_schemas.UserResponse.model_validate(current_user)


@router.get("/me/role")
async def get_current_user_role(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> dict[str, str | None]:
    """Return current user's active role."""
    return {"role": current_user.role}


@router.get("/me/roles", response_model=user_schemas.UserRolesResponse)
async def get_current_user_roles(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.UserRolesResponse:
    """Return active and enabled roles for the current user."""
    result = await auth_service.get_roles(current_user.id)
    if result is None:
        raise http_errors.not_found("User not found")
    return result


@router.post("/me/role", response_model=user_schemas.UserRolesResponse)
async def switch_my_role(
    payload: user_schemas.RoleSwitchRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.UserRolesResponse:
    """Switch the active role for the current user.

    Creates the target role profile if it does not exist yet.
    """
    result = await auth_service.switch_role(current_user.id, payload.role)
    if result is None:
        raise http_errors.not_found("User not found")
    return result
