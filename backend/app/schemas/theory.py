"""
Theory content schemas (subjects/sections/subsections/materials).
"""

import datetime as dt

import pydantic


class SubjectResponse(pydantic.BaseModel):
    id: int
    name: str
    description: str | None
    icon_url: str | None
    order_number: int
    is_active: bool
    created_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class SectionResponse(pydantic.BaseModel):
    id: int
    subject_id: int
    name: str
    description: str | None
    order_number: int
    created_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class SubsectionResponse(pydantic.BaseModel):
    id: int
    section_id: int
    name: str
    description: str | None
    order_number: int
    created_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class TheoryMaterialResponse(pydantic.BaseModel):
    id: int
    subsection_id: int
    title: str
    content: str
    order_number: int
    estimated_read_time: int | None
    is_published: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)

