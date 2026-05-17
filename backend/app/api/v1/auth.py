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
    return user_schemas.UserResponse.model_validate(current_user)
