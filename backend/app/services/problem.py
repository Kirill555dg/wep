"""
Problem service.

Manages problem creation, retrieval, update and deletion.

Failure semantics:
  - Lookup-style methods (``get_problem_by_id``) return ``None`` if the
    problem is missing. Routes translate ``None`` into HTTP 404.
  - ``update_problem`` and ``delete_problem`` return ``None`` / ``False``
    when the problem does not exist.
"""

import typing as tp

from app.core import pagination as core_pagination
from app.repositories import homework as homework_repository
from app.schemas import homework as homework_schemas


class ProblemService:
    """Service for managing problems."""

    def __init__(self, problem_repo: homework_repository.ProblemRepository):
        self.problem_repo = problem_repo

    async def create_problem(
        self,
        problem_data: homework_schemas.ProblemCreate,
        teacher_id: int,
    ) -> tp.Any:
        """Create a new problem."""
        data = problem_data.model_dump()
        if "difficulty" in data and data["difficulty"] is not None:
            try:
                data["difficulty"] = int(data["difficulty"])
            except (TypeError, ValueError):
                data["difficulty"] = 1
        data["problem_type"] = str(data.get("problem_type", "text"))

        return await self.problem_repo.create(data)

    async def get_all_problems(
        self,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[tp.Any]:
        """Return problems with pagination."""
        return await self.problem_repo.get_all(skip, limit)

    async def count_all_problems(self) -> int:
        return await self.problem_repo.count()

    async def get_problem_by_id(self, problem_id: int) -> tp.Any | None:
        """Return a problem by id, or ``None`` if not found."""
        return await self.problem_repo.get_by_id(problem_id)

    async def update_problem(
        self,
        problem_id: int,
        problem_data: homework_schemas.ProblemUpdate,
        teacher_id: int,
    ) -> tp.Any | None:
        """Update a problem; returns ``None`` if it does not exist."""
        data = problem_data.model_dump(exclude_unset=True)
        if "difficulty" in data:
            try:
                data["difficulty"] = int(data["difficulty"]) if data["difficulty"] is not None else None
            except (TypeError, ValueError):
                data["difficulty"] = None
        if "problem_type" in data and data["problem_type"] is not None:
            data["problem_type"] = str(data["problem_type"])

        return await self.problem_repo.update(problem_id, data)

    async def delete_problem(self, problem_id: int, teacher_id: int) -> bool:
        """Delete a problem; returns ``False`` if it does not exist."""
        return await self.problem_repo.delete(problem_id)
