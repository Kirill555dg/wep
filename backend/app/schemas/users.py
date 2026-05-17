import datetime as dt

import pydantic


class UserBase(pydantic.BaseModel):
    email: pydantic.EmailStr
    first_name: str = pydantic.Field(..., min_length=1, max_length=100)
    last_name: str = pydantic.Field(..., min_length=1, max_length=100)
    middle_name: str | None = pydantic.Field(default=None, max_length=100)
    avatar_url: str | None = None
    username: str | None = pydantic.Field(default=None, min_length=3, max_length=100)
    full_name: str | None = pydantic.Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = pydantic.Field(..., min_length=8, max_length=128)


class UserUpdate(pydantic.BaseModel):
    username: str | None = pydantic.Field(default=None, min_length=3, max_length=100)
    email: pydantic.EmailStr | None = None
    first_name: str | None = pydantic.Field(default=None, min_length=1, max_length=100)
    last_name: str | None = pydantic.Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = pydantic.Field(default=None, max_length=100)
    full_name: str | None = pydantic.Field(default=None, max_length=255)
    avatar_url: str | None = None
    is_active: bool | None = None


class UserResponse(pydantic.BaseModel):
    id: int
    email: pydantic.EmailStr
    first_name: str
    last_name: str
    middle_name: str | None = None
    username: str | None = None
    full_name: str | None = None
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    hashed_password: str


class LoginRequest(pydantic.BaseModel):
    username_or_email: str
    password: str


class UserLogin(LoginRequest):
    pass


class TokenResponse(pydantic.BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
