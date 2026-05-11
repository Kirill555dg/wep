"""
Authentication endpoints
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.models import users as user_models
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module

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
    """
    Register new user (student or teacher)

    - **email**: Valid email address
    - **password**: Password (min 8 characters)
    - **first_name / last_name / middle_name**: User's name parts
    - **role**: Initial active role ("student" | "teacher")
    """
    return await auth_service.register_user(user_data)


@router.post("/login", response_model=user_schemas.TokenResponse)
async def login(
    credentials: user_schemas.LoginRequest,
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.TokenResponse:
    """
    Authenticate user and get JWT token

    - **username_or_email**: Username or email
    - **password**: User password

    Returns JWT access token and user data
    """
    token = await auth_service.authenticate(credentials)
    if not token:
        raise fastapi.HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username/email or password",
        )
    return token


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_profile(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> user_schemas.UserResponse:
    """
    Get current authenticated user profile

    Requires valid JWT token in Authorization header
    """
    return user_schemas.UserResponse.model_validate(current_user)


@router.get("/me/role")
async def get_current_user_role(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
) -> dict[str, str | None]:
    """
    Get current user's role (teacher or student)

    Returns: {"role": "teacher"} or {"role": "student"}
    """
    return {"role": current_user.role}


@router.get("/me/roles", response_model=user_schemas.UserRolesResponse)
async def get_current_user_roles(
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.UserRolesResponse:
    """
    Get active role + enabled roles for current user.
    """
    return await auth_service.get_roles(current_user.id)


@router.post("/me/role", response_model=user_schemas.UserRolesResponse)
async def switch_my_role(
    payload: user_schemas.RoleSwitchRequest,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    auth_service: auth_service_module.AuthService = fastapi.Depends(deps.get_auth_service),
) -> user_schemas.UserRolesResponse:
    """
    Switch active role for current user.

    If target role profile does not exist, it will be created.
    """
    return await auth_service.switch_role(current_user.id, payload.role)
