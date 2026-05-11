"""
Homework, Problem, and Statistics repositories
"""

import typing as tp

import sqlalchemy as sa
from sqlalchemy import orm as orm
from sqlalchemy.ext import asyncio as sa_asyncio

from app.models import classes as classes_models
from app.models import homework as homework_models
from app.models import problems as problem_models
from app.repositories import base as base_repository


class HomeworkRepository(base_repository.BaseRepository[homework_models.Homework]):
    """Repository for Homework operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(homework_models.Homework, db)

    async def get_by_lesson(
        self, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> list[homework_models.Homework]:
        """Get homeworks for lesson"""
        stmt = (
            sa.select(homework_models.Homework)
            .where(homework_models.Homework.lesson_id == lesson_id)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[homework_models.Homework], items)

    async def get_published(
        self, lesson_id: int, skip: int = 0, limit: int = 100
    ) -> list[homework_models.Homework]:
        """Get published homeworks for lesson"""
        stmt = (
            sa.select(homework_models.Homework)
            .where(
                homework_models.Homework.lesson_id == lesson_id,
                homework_models.Homework.is_published,
            )
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[homework_models.Homework], items)

    async def get_with_problems(self, homework_id: int) -> homework_models.Homework | None:
        """Get homework with problems"""
        stmt = (
            sa.select(homework_models.Homework)
            .options(orm.joinedload(homework_models.Homework.homework_problems))
            .where(homework_models.Homework.id == homework_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(homework_models.Homework | None, obj)

    async def count_by_lesson(self, lesson_id: int) -> int:
        """Count homeworks in lesson"""
        stmt = (
            sa.select(sa.func.count())
            .select_from(homework_models.Homework)
            .where(homework_models.Homework.lesson_id == lesson_id)
        )
        result = await self.db.execute(stmt)
        count_value = result.scalar_one()
        return tp.cast(int, count_value)

    async def count_published_by_lesson(self, lesson_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(homework_models.Homework)
            .where(
                homework_models.Homework.lesson_id == lesson_id,
                homework_models.Homework.is_published,
            )
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)


class HomeworkProblemRepository(base_repository.BaseRepository[homework_models.HomeworkProblem]):
    """Repository for HomeworkProblem operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(homework_models.HomeworkProblem, db)

    async def get_by_homework(self, homework_id: int) -> list[homework_models.HomeworkProblem]:
        """Get problems for homework"""
        stmt = (
            sa.select(homework_models.HomeworkProblem)
            .where(homework_models.HomeworkProblem.homework_id == homework_id)
            .order_by(homework_models.HomeworkProblem.order_number)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[homework_models.HomeworkProblem], items)

    async def add_problem_to_homework(
        self, homework_id: int, problem_id: int, points: float = 10.0, order_number: int = 0
    ) -> homework_models.HomeworkProblem:
        """Add problem to homework"""
        return await self.create(
            {
                "homework_id": homework_id,
                "problem_id": problem_id,
                "points": points,
                "order_number": order_number,
            }
        )

    async def remove_problem_from_homework(self, homework_id: int, problem_id: int) -> bool:
        """Remove problem from homework"""
        stmt = sa.select(homework_models.HomeworkProblem).where(
            homework_models.HomeworkProblem.homework_id == homework_id,
            homework_models.HomeworkProblem.problem_id == problem_id,
        )
        hw_problem = await self._scalar_one_or_none(stmt)

        if not hw_problem:
            return False

        await self.db.delete(hw_problem)
        await self.db.commit()
        return True


class ProblemRepository(base_repository.BaseRepository[problem_models.Problem]):
    """Repository for Problem operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(problem_models.Problem, db)

    async def get_by_type(
        self, problem_type: str, skip: int = 0, limit: int = 100
    ) -> list[problem_models.Problem]:
        """Get problems by type"""
        stmt = (
            sa.select(problem_models.Problem)
            .where(problem_models.Problem.problem_type == problem_type)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[problem_models.Problem], items)

    async def get_by_difficulty(
        self, difficulty: int, skip: int = 0, limit: int = 100
    ) -> list[problem_models.Problem]:
        """Get problems by difficulty"""
        stmt = (
            sa.select(problem_models.Problem)
            .where(problem_models.Problem.difficulty == difficulty)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[problem_models.Problem], items)

    async def get_published(
        self, skip: int = 0, limit: int = 100
    ) -> list[problem_models.Problem]:
        """Get published problems"""
        stmt = (
            sa.select(problem_models.Problem)
            .where(problem_models.Problem.is_published)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[problem_models.Problem], items)


class StatisticsRepository(base_repository.BaseRepository[homework_models.Statistics]):
    """Repository for Statistics operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(homework_models.Statistics, db)

    async def get_by_student(
        self, student_id: int, skip: int = 0, limit: int = 100
    ) -> list[homework_models.Statistics]:
        """Get statistics for student"""
        stmt = (
            sa.select(homework_models.Statistics)
            .where(homework_models.Statistics.student_id == student_id)
            .order_by(homework_models.Statistics.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[homework_models.Statistics], items)

    async def get_by_homework(
        self, homework_id: int, skip: int = 0, limit: int = 100
    ) -> list[homework_models.Statistics]:
        """Get statistics for homework"""
        stmt = (
            sa.select(homework_models.Statistics)
            .where(homework_models.Statistics.homework_id == homework_id)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[homework_models.Statistics], items)

    async def count_by_student(self, student_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(homework_models.Statistics)
            .where(homework_models.Statistics.student_id == student_id)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)

    async def count_by_homework(self, homework_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(homework_models.Statistics)
            .where(homework_models.Statistics.homework_id == homework_id)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)

    async def get_student_homework_stats(
        self, student_id: int, homework_id: int
    ) -> homework_models.Statistics | None:
        """Get specific student homework statistics"""
        stmt = sa.select(homework_models.Statistics).where(
            homework_models.Statistics.student_id == student_id,
            homework_models.Statistics.homework_id == homework_id,
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(homework_models.Statistics | None, obj)

    async def get_or_create_stats(
        self, student_id: int, homework_id: int, max_score: float
    ) -> homework_models.Statistics:
        """Get existing or create new statistics"""
        stats = await self.get_student_homework_stats(student_id, homework_id)
        if stats:
            return stats

        return await self.create(
            {
                "student_id": student_id,
                "homework_id": homework_id,
                "max_score": max_score,
                "score": 0.0,
                "status": "not_started",
            }
        )

    async def update_score(
        self,
        stats_id: int,
        score: float,
        status: str = "in_progress",
    ) -> homework_models.Statistics | None:
        """Update statistics score"""
        return await self.update(stats_id, {"score": score, "status": status})

    async def submit_homework(self, stats_id: int) -> homework_models.Statistics | None:
        """Mark homework as submitted"""
        return await self.update(
            stats_id,
            {
                "status": "submitted",
                "submitted_at": tp.cast(tp.Any, "NOW()"),  # PostgreSQL function
            },
        )

    async def get_average_score_by_homework(self, homework_id: int) -> float:
        """Calculate average score for homework"""
        stmt = sa.select(sa.func.avg(homework_models.Statistics.score)).where(
            homework_models.Statistics.homework_id == homework_id,
            homework_models.Statistics.status.in_(["submitted", "graded"]),
        )
        avg_value = await self._scalar_one_or_none(stmt)
        return float(avg_value) if avg_value else 0.0

    async def get_student_progress_summary(self, student_id: int) -> dict[str, tp.Any]:
        """Aggregate student progress in a single SQL query."""
        completed_statuses = [
            homework_models.HomeworkStatus.SUBMITTED,
            homework_models.HomeworkStatus.GRADED,
        ]

        stmt = sa.select(
            sa.func.count(homework_models.Statistics.id).label("total_homeworks"),
            sa.func.count(
                sa.case((homework_models.Statistics.status.in_(completed_statuses), 1))
            ).label("completed"),
            sa.func.count(
                sa.case(
                    (homework_models.Statistics.status == homework_models.HomeworkStatus.IN_PROGRESS, 1)
                )
            ).label("in_progress"),
            sa.func.count(
                sa.case(
                    (homework_models.Statistics.status == homework_models.HomeworkStatus.NOT_STARTED, 1)
                )
            ).label("not_started"),
            sa.func.coalesce(sa.func.sum(homework_models.Statistics.attempts_count), 0).label("total_attempts"),
            sa.func.coalesce(sa.func.sum(homework_models.Statistics.time_spent_minutes), 0).label(
                "total_time_spent_minutes"
            ),
            sa.func.coalesce(
                sa.func.sum(
                    sa.case(
                        (homework_models.Statistics.status == homework_models.HomeworkStatus.GRADED, homework_models.Statistics.score),
                        else_=0.0,
                    )
                ),
                0.0,
            ).label("graded_score_sum"),
            sa.func.coalesce(
                sa.func.sum(
                    sa.case(
                        (homework_models.Statistics.status == homework_models.HomeworkStatus.GRADED, homework_models.Statistics.max_score),
                        else_=0.0,
                    )
                ),
                0.0,
            ).label("graded_max_sum"),
        ).where(homework_models.Statistics.student_id == student_id)

        row = (await self.db.execute(stmt)).one()
        total_homeworks = tp.cast(int, row.total_homeworks)
        completed = tp.cast(int, row.completed)
        in_progress = tp.cast(int, row.in_progress)
        not_started = tp.cast(int, row.not_started)
        total_attempts = tp.cast(int, row.total_attempts)
        total_time_spent_minutes = tp.cast(int, row.total_time_spent_minutes)
        graded_score_sum = float(row.graded_score_sum)
        graded_max_sum = float(row.graded_max_sum)
        avg_score_pct = (graded_score_sum / graded_max_sum * 100.0) if graded_max_sum > 0 else 0.0

        return {
            "total_homeworks": total_homeworks,
            "completed": completed,
            "in_progress": in_progress,
            "not_started": not_started,
            "average_score_percentage": round(avg_score_pct, 2),
            "total_attempts": total_attempts,
            "total_time_spent_minutes": total_time_spent_minutes,
        }

    async def get_classroom_progress_summary(self, classroom_id: int) -> dict[str, int]:
        """Aggregate classroom progress in a single SQL query."""
        completed_statuses = [
            homework_models.HomeworkStatus.SUBMITTED,
            homework_models.HomeworkStatus.GRADED,
        ]

        # Note: `statistics.student_id` is a Student.id (not User.id),
        # so we join via student_classrooms.student_id.
        stmt = (
            sa.select(
                sa.func.count(sa.distinct(classes_models.StudentClassroom.student_id)).label("total_students"),
                sa.func.count(homework_models.Statistics.id).label("total_homeworks_assigned"),
                sa.func.count(
                    sa.case((homework_models.Statistics.status.in_(completed_statuses), 1))
                ).label("completed_homeworks"),
            )
            .select_from(classes_models.StudentClassroom)
            .join(
                homework_models.Statistics,
                homework_models.Statistics.student_id == classes_models.StudentClassroom.student_id,
                isouter=True,
            )
            .where(
                classes_models.StudentClassroom.classroom_id == classroom_id,
                classes_models.StudentClassroom.is_active,
            )
        )

        row = (await self.db.execute(stmt)).one()
        return {
            "total_students": tp.cast(int, row.total_students),
            "total_homeworks_assigned": tp.cast(int, row.total_homeworks_assigned),
            "completed_homeworks": tp.cast(int, row.completed_homeworks),
        }
