"""
Error response schemas for API clients.
"""

import typing as tp

import pydantic


class ErrorBody(pydantic.BaseModel):
    code: str
    message: str
    meta: dict[str, tp.Any] = pydantic.Field(default_factory=dict)


class ErrorResponse(pydantic.BaseModel):
    error: ErrorBody
    request_id: str

