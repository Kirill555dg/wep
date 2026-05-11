"""
User Pydantic schemas (DTOs)
"""

import enum

import datetime as dt
import pydantic


class UserRole(str, enum.Enum):
    """User roles"""

    TEACHER = "teacher"
    STUDENT = "student"


# Base schemas
class UserBase(pydantic.BaseModel):
    """Base user fields"""

    email: pydantic.EmailStr
    first_name: str = pydantic.Field(..., min_length=1, max_length=100)
    last_name: str = pydantic.Field(..., min_length=1, max_length=100)
    middle_name: str | None = pydantic.Field(default=None, max_length=100)
    role: UserRole = UserRole.STUDENT
    avatar_url: str | None = None
    username: str | None = pydantic.Field(default=None, min_length=3, max_length=100)
    full_name: str | None = pydantic.Field(default=None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = pydantic.Field(..., min_length=8, max_length=128)


class RoleSwitchRequest(pydantic.BaseModel):
    role: UserRole


class UserRolesResponse(pydantic.BaseModel):
    active_role: UserRole
    enabled_roles: list[UserRole]


class UserUpdate(pydantic.BaseModel):
    """Schema for updating a user"""

    username: str | None = pydantic.Field(default=None, min_length=3, max_length=100)
    email: pydantic.EmailStr | None = None
    first_name: str | None = pydantic.Field(default=None, min_length=1, max_length=100)
    last_name: str | None = pydantic.Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = pydantic.Field(default=None, max_length=100)
    full_name: str | None = pydantic.Field(default=None, max_length=255)
    avatar_url: str | None = None
    is_active: bool | None = None


class UserResponse(pydantic.BaseModel):
    """Schema for user response"""

    id: int
    email: pydantic.EmailStr
    first_name: str
    last_name: str
    middle_name: str | None = None
    role: UserRole
    username: str | None = None
    full_name: str | None = None
    is_active: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """User model with sensitive data"""

    hashed_password: str


# Teacher schemas
class TeacherBase(pydantic.BaseModel):
    """Base teacher fields"""

    bio: str | None = None
    subject_specialization: str | None = None
    years_of_experience: int = pydantic.Field(default=0, ge=0)


class TeacherCreate(TeacherBase):
    """Schema for creating a teacher (used internally)"""

    user_id: int


class TeacherUpdate(TeacherBase):
    """Schema for updating a teacher"""

    pass


class TeacherResponse(TeacherBase):
    """Schema for teacher response"""

    id: int
    user_id: int
    rating: int
    user: UserResponse  # Nested user data

    model_config = pydantic.ConfigDict(from_attributes=True)


# Student schemas
class StudentBase(pydantic.BaseModel):
    """Base student fields"""

    grade_level: int | None = pydantic.Field(None, ge=1, le=12)
    student_id_number: str | None = None


class StudentCreate(StudentBase):
    """Schema for creating a student (used internally)"""

    user_id: int


class StudentUpdate(StudentBase):
    """Schema for updating a student"""

    pass


class StudentResponse(StudentBase):
    """Schema for student response"""

    id: int
    user_id: int
    enrollment_date: dt.datetime
    user: UserResponse  # Nested user data

    model_config = pydantic.ConfigDict(from_attributes=True)


# Authentication schemas
class LoginRequest(pydantic.BaseModel):
    """Login request schema"""

    username_or_email: str
    password: str


class UserLogin(LoginRequest):
    """Alias for backward compatibility"""


class TokenResponse(pydantic.BaseModel):
    """Token response schema"""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
