"""
Pagination schemas.
"""

import typing as tp

import pydantic


T = tp.TypeVar("T")


class Page(pydantic.BaseModel, tp.Generic[T]):
    items: list[T]
    total: int
    skip: int
    limit: int

