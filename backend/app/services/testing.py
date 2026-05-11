"""
Testing service for answer checking and grading.

Failure semantics:
  - ``submit_answer`` and ``submit_homework`` raise :class:`ServiceError`
    for orchestrated failures (missing student profile, problem absent in
    homework, homework or problem missing).
  - ``get_homework_status`` returns ``None`` when there are no attempts yet,
    so the route can decide what HTTP code to return.
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.repositories import homework as homework_repository
from app.repositories import user as user_repository
from app.schemas import homework as homework_schemas
from app.services import exceptions as service_exceptions


class TestingService:
    """Service for testing and grading.

    Handles answer submission, automatic checking and statistics updates.
    """

    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.homework_repo = homework_repository.HomeworkRepository(db)
        self.problem_repo = homework_repository.ProblemRepository(db)
        self.stats_repo = homework_repository.StatisticsRepository(db)
        self.hw_problem_repo = homework_repository.HomeworkProblemRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def submit_answer(
        self,
        answer_data: homework_schemas.AnswerSubmit,
        student_user_id: int,
    ) -> homework_schemas.StatisticsResponse:
        """Submit answer for a problem and run auto-check.

        Raises ``ServiceError`` with codes ``forbidden``, ``homework_not_found``,
        ``problem_not_found`` or ``problem_not_in_homework``.
        """
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise service_exceptions.ServiceError(
                "Only students can submit answers", code="forbidden",
            )

        homework = await self.homework_repo.get_by_id(answer_data.homework_id)
        if not homework:
            raise service_exceptions.ServiceError(
                "Homework not found", code="homework_not_found",
            )

        problem = await self.problem_repo.get_by_id(answer_data.problem_id)
        if not problem:
            raise service_exceptions.ServiceError(
                "Problem not found", code="problem_not_found",
            )

        hw_problems = await self.hw_problem_repo.get_by_homework(answer_data.homework_id)
        hw_problem = next(
            (hp for hp in hw_problems if hp.problem_id == answer_data.problem_id), None,
        )
        if not hw_problem:
            raise service_exceptions.ServiceError(
                "Problem not in this homework", code="problem_not_in_homework",
            )

        stats = await self.stats_repo.get_or_create_stats(
            student.id, answer_data.homework_id, homework.max_score,
        )

        is_correct = self._check_answer(answer_data.answer, problem.correct_answer)
        if is_correct:
            new_score = min(stats.score + hw_problem.points, stats.max_score)
        else:
            new_score = stats.score

        updated_stats = await self.stats_repo.update(
            stats.id,
            {
                "score": new_score,
                "status": "in_progress",
                "attempts_count": stats.attempts_count + 1,
                "time_spent_minutes": stats.time_spent_minutes + answer_data.time_spent_minutes,
            },
        )
        assert updated_stats is not None  # stats existence guaranteed above
        return homework_schemas.StatisticsResponse.model_validate(updated_stats)

    async def submit_homework(
        self,
        homework_id: int,
        student_user_id: int,
    ) -> homework_schemas.StatisticsResponse:
        """Submit a homework for grading.

        Raises ``ServiceError`` with codes ``forbidden`` (missing student
        profile) or ``no_attempts`` (no attempts to submit).
        """
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise service_exceptions.ServiceError(
                "Only students can submit homework", code="forbidden",
            )

        stats = await self.stats_repo.get_student_homework_stats(student.id, homework_id)
        if not stats:
            raise service_exceptions.ServiceError(
                "No attempts found for this homework", code="no_attempts",
            )

        updated_stats = await self.stats_repo.submit_homework(stats.id)
        assert updated_stats is not None  # stats existence guaranteed above
        return homework_schemas.StatisticsResponse.model_validate(updated_stats)

    def _check_answer(self, student_answer: str, correct_answer: str | None) -> bool:
        """Return True if the answer matches the reference (case-insensitive)."""
        if not correct_answer:
            return False
        return student_answer.strip().lower() == correct_answer.strip().lower()

    async def get_homework_status(
        self,
        homework_id: int,
        student_user_id: int,
    ) -> homework_schemas.StatisticsResponse | None:
        """Return current attempt statistics or ``None`` if there are no attempts."""
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return None

        stats = await self.stats_repo.get_student_homework_stats(student.id, homework_id)
        if not stats:
            return None

        return homework_schemas.StatisticsResponse.model_validate(stats)
