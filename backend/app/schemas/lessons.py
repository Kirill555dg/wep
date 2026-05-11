"""
Lesson Pydantic schemas (DTOs)
"""

import datetime as dt

import pydantic


class LessonBase(pydantic.BaseModel):
    """Base lesson fields"""

    title: str = pydantic.Field(..., min_length=1, max_length=255)
    description: str | None = None
    order_number: int | None = pydantic.Field(None, ge=0)
    scheduled_at: dt.datetime | None = None


class LessonCreate(LessonBase):
    """Schema for creating a lesson"""

    classroom_id: int
    theory_material_ids: list[int] = pydantic.Field(default_factory=list)


class LessonUpdate(pydantic.BaseModel):
    """Schema for updating a lesson"""

    title: str | None = pydantic.Field(None, min_length=1, max_length=255)
    description: str | None = None
    order_number: int | None = pydantic.Field(None, ge=0)
    scheduled_at: dt.datetime | None = None
    is_published: bool | None = None


class LessonResponse(LessonBase):
    """Schema for lesson response"""

    id: int
    classroom_id: int
    is_published: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class LessonDetailResponse(LessonResponse):
    """Detailed lesson response with materials"""

    materials_count: int = 0
    homeworks_count: int = 0


# Theory Material schemas
class TheoryMaterialBase(pydantic.BaseModel):
    """Base theory material fields"""

    title: str = pydantic.Field(..., min_length=1, max_length=255)
    content: str = pydantic.Field(..., min_length=1)
    order_number: int = pydantic.Field(default=0, ge=0)
    estimated_read_time: int | None = pydantic.Field(None, ge=1)


class TheoryMaterialCreate(TheoryMaterialBase):
    """Schema for creating theory material"""

    subsection_id: int


class TheoryMaterialUpdate(pydantic.BaseModel):
    """Schema for updating theory material"""

    title: str | None = pydantic.Field(None, min_length=1, max_length=255)
    content: str | None = pydantic.Field(None, min_length=1)
    order_number: int | None = pydantic.Field(None, ge=0)
    estimated_read_time: int | None = pydantic.Field(None, ge=1)
    is_published: bool | None = None


class TheoryMaterialResponse(TheoryMaterialBase):
    """Schema for theory material response"""

    id: int
    subsection_id: int
    is_published: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)
