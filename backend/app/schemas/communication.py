"""
Chat and messages schemas.
"""

import datetime as dt

import pydantic

from app.schemas import users as user_schemas


class UserPublic(pydantic.BaseModel):
    id: int
    first_name: str
    last_name: str
    full_name: str
    avatar_url: str | None
    role: user_schemas.UserRole

    model_config = pydantic.ConfigDict(from_attributes=True)


class MessageCreate(pydantic.BaseModel):
    content: str = pydantic.Field(..., min_length=1, max_length=5000)


class MessageResponse(pydantic.BaseModel):
    id: int
    chat_id: int
    sender_id: int
    sender: UserPublic | None = None
    content: str
    is_edited: bool
    is_deleted: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)

