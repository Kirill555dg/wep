"""
Problem Service
Manages problem creation, retrieval, and management
"""

import typing as tp

from app.domain import errors as domain_errors
from app.core import pagination as core_pagination
from app.repositories import homework as homework_repository
from app.schemas import homework as homework_schemas


class ProblemService:
    """Service for managing problems"""

    def __init__(self, problem_repo: homework_repository.ProblemRepository):
        self.problem_repo = problem_repo

    async def create_problem(
        self,
        problem_data: homework_schemas.ProblemCreate,
        teacher_id: int,
    ) -> tp.Any:
        """
        Create a new problem

        Args:
            problem_data: Problem data
            teacher_id: ID of the teacher creating the problem

        Returns:
            Created problem
        """
        # Convert Pydantic model to dict
        data = problem_data.model_dump()
        if "difficulty" in data and data["difficulty"] is not None:
            try:
                data["difficulty"] = int(data["difficulty"])
            except (TypeError, ValueError):
                data["difficulty"] = 1
        data["problem_type"] = str(data.get("problem_type", "text"))

        # Create problem
        problem = await self.problem_repo.create(data)
        return problem

    async def get_all_problems(
        self,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[tp.Any]:
        """
        Get all problems

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of problems
        """
        return await self.problem_repo.get_all(skip, limit)

    async def count_all_problems(self) -> int:
        return await self.problem_repo.count()

    async def get_problem_by_id(self, problem_id: int) -> tp.Any | None:
        """
        Get problem by ID

        Args:
            problem_id: Problem ID

        Returns:
            Problem if found, None otherwise
        """
        problem = await self.problem_repo.get_by_id(problem_id)
        if not problem:
            raise domain_errors.NotFoundError("Problem not found")
        return problem

    async def update_problem(
        self, problem_id: int, problem_data: homework_schemas.ProblemUpdate, teacher_id: int
    ) -> tp.Any:
        """
        Update a problem

        Args:
            problem_id: Problem ID
            problem_data: Updated problem data
            teacher_id: ID of the teacher updating the problem

        Returns:
            Updated problem

        Raises:
            HTTPException: If problem not found
        """
        # Convert Pydantic model to dict, excluding unset fields
        data = problem_data.model_dump(exclude_unset=True)
        if "difficulty" in data:
            try:
                data["difficulty"] = int(data["difficulty"]) if data["difficulty"] is not None else None
            except (TypeError, ValueError):
                data["difficulty"] = None
        if "problem_type" in data and data["problem_type"] is not None:
            data["problem_type"] = str(data["problem_type"])

        # Update problem
        problem = await self.problem_repo.update(problem_id, data)
        if not problem:
            raise domain_errors.NotFoundError("Problem not found")
        return problem

    async def delete_problem(self, problem_id: int, teacher_id: int) -> bool:
        """
        Delete a problem

        Args:
            problem_id: Problem ID
            teacher_id: ID of the teacher deleting the problem

        Returns:
            True if deleted successfully

        Raises:
            HTTPException: If problem not found
        """
        success = await self.problem_repo.delete(problem_id)
        if not success:
            raise domain_errors.NotFoundError("Problem not found")
        return True
