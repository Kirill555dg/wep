"""
API pagination dependency.

Provides consistent skip/limit defaults and validation for all endpoints.
"""

import dataclasses as dc

import fastapi

from app.core import pagination as core_pagination


@dc.dataclass(frozen=True, slots=True)
class Pagination:
    skip: int
    limit: int


def get_pagination(
    skip: int = fastapi.Query(core_pagination.DEFAULT_SKIP, ge=0),
    limit: int = fastapi.Query(core_pagination.DEFAULT_LIMIT, ge=1, le=core_pagination.MAX_LIMIT),
) -> Pagination:
    return Pagination(skip=skip, limit=limit)

