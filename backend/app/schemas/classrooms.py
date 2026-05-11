"""
Classroom Pydantic schemas (DTOs)
"""

import datetime as dt

import pydantic

from app.schemas import communication as communication_schemas


class ClassroomBase(pydantic.BaseModel):
    """Base classroom fields"""

    name: str = pydantic.Field(..., min_length=1, max_length=255)
    description: str | None = None
    subject: str = pydantic.Field(..., min_length=1, max_length=100)
    grade_level: int | None = pydantic.Field(None, ge=1, le=12)
    max_students: int = pydantic.Field(default=30, ge=1, le=100)


class ClassroomCreate(ClassroomBase):
    """Schema for creating a classroom"""

    pass  # teacher_id will be taken from authenticated user


class ClassroomUpdate(pydantic.BaseModel):
    """Schema for updating a classroom"""

    name: str | None = pydantic.Field(None, min_length=1, max_length=255)
    description: str | None = None
    subject: str | None = pydantic.Field(None, min_length=1, max_length=100)
    grade_level: int | None = pydantic.Field(None, ge=1, le=12)
    max_students: int | None = pydantic.Field(None, ge=1, le=100)
    is_active: bool | None = None


class ClassroomResponse(ClassroomBase):
    """Schema for classroom response"""

    id: int
    teacher_id: int
    is_active: bool
    invite_code: str | None
    created_at: dt.datetime
    updated_at: dt.datetime
    students_count: int = 0  # Calculated field

    model_config = pydantic.ConfigDict(from_attributes=True)


class ClassroomDetailResponse(ClassroomResponse):
    """Detailed classroom response with nested data"""

    # Can include teacher, students list, etc.
    pass


class ClassroomStudentResponse(pydantic.BaseModel):
    student_id: int
    user: communication_schemas.UserPublic
    enrolled_at: dt.datetime
    grade_level: int | None

# Invite schemas
class InviteCreate(pydantic.BaseModel):
    """Schema for creating an invite"""

    classroom_id: int
    max_uses: int | None = pydantic.Field(default=1, ge=1)
    expires_at: dt.datetime | None = None


class InviteResponse(pydantic.BaseModel):
    """Schema for invite response"""

    id: int
    classroom_id: int
    invite_code: str
    max_uses: int | None
    uses_count: int
    status: str
    expires_at: dt.datetime | None
    created_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class JoinClassroomRequest(pydantic.BaseModel):
    """Schema for joining classroom via invite code"""

    invite_code: str
