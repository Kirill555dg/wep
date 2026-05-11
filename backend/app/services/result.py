"""
Result service for aggregating student progress.

Lookup-style methods that depend on a student profile return ``None`` when
the profile is missing; the route translates this into HTTP 404.
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import pagination as core_pagination
from app.repositories import classroom as classroom_repository
from app.repositories import homework as homework_repository
from app.repositories import user as user_repository
from app.schemas import homework as homework_schemas
from app.schemas import progress as progress_schemas


class ResultService:
    """
    Service for aggregating and analyzing results

    Handles progress tracking, statistics aggregation
    """

    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.stats_repo = homework_repository.StatisticsRepository(db)
        self.homework_repo = homework_repository.HomeworkRepository(db)
        self.student_classroom_repo = classroom_repository.StudentClassroomRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def get_student_statistics(
        self,
        student_user_id: int,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[homework_schemas.StatisticsResponse] | None:
        """Return all statistics for a student, or ``None`` if profile missing."""
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return None

        stats = await self.stats_repo.get_by_student(student.id, skip, limit)
        return [homework_schemas.StatisticsResponse.model_validate(s) for s in stats]

    async def count_student_statistics(self, student_user_id: int) -> int | None:
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return None
        return await self.stats_repo.count_by_student(student.id)

    async def get_homework_statistics(
        self,
        homework_id: int,
        teacher_user_id: int,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[homework_schemas.StatisticsResponse]:
        """
        Get statistics for all students for a homework (teacher only)

        Args:
            homework_id: Homework ID
            teacher_user_id: User ID of teacher
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of statistics

        Raises:
            HTTPException: If not authorized
        """
        # Note: Authorization check would happen here
        # For now, returning all stats

        stats = await self.stats_repo.get_by_homework(homework_id, skip, limit)
        return [homework_schemas.StatisticsResponse.model_validate(s) for s in stats]

    async def count_homework_statistics(self, homework_id: int) -> int:
        return await self.stats_repo.count_by_homework(homework_id)

    async def get_student_progress(
        self, student_user_id: int,
    ) -> progress_schemas.StudentProgressResponse | None:
        """Return overall student progress, or ``None`` if profile is missing."""
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return None

        summary = await self.stats_repo.get_student_progress_summary(student.id)
        return progress_schemas.StudentProgressResponse.model_validate(summary)

    async def get_classroom_progress(
        self, classroom_id: int, teacher_user_id: int
    ) -> progress_schemas.ClassroomProgressResponse:
        """
        Get progress summary for classroom (teacher only)

        Args:
            classroom_id: Classroom ID
            teacher_user_id: User ID of teacher

        Returns:
            Classroom progress summary
        """
        summary = await self.stats_repo.get_classroom_progress_summary(classroom_id)

        total_students = summary["total_students"]
        total_homeworks_assigned = summary["total_homeworks_assigned"]
        completed_homeworks = summary["completed_homeworks"]

        completion_rate = (
            completed_homeworks / total_homeworks_assigned * 100.0
            if total_homeworks_assigned > 0
            else 0.0
        )

        return progress_schemas.ClassroomProgressResponse(
            total_students=total_students,
            total_homeworks_assigned=total_homeworks_assigned,
            completed_homeworks=completed_homeworks,
            average_completion_rate=round(completion_rate, 2),
        )
