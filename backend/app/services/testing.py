"""
Testing service for answer checking and grading
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.domain import errors as domain_errors
from app.repositories import homework as homework_repository
from app.repositories import user as user_repository
from app.schemas import homework as homework_schemas


class TestingService:
    """
    Service for testing and grading

    Handles answer submission, automatic checking, and statistics updates
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
        """
        Submit answer for a problem

        Args:
            answer_data: Submitted answer data
            student_user_id: User ID of student

        Returns:
            Updated statistics

        Raises:
            DomainError: If not authorized or validation fails
        """
        # Verify student
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise domain_errors.ForbiddenError("Only students can submit answers")

        # Verify homework and problem exist
        homework = await self.homework_repo.get_by_id(answer_data.homework_id)
        if not homework:
            raise domain_errors.NotFoundError("Homework not found")

        problem = await self.problem_repo.get_by_id(answer_data.problem_id)
        if not problem:
            raise domain_errors.NotFoundError("Problem not found")

        # Check if problem is in homework
        hw_problems = await self.hw_problem_repo.get_by_homework(answer_data.homework_id)
        hw_problem = next(
            (hp for hp in hw_problems if hp.problem_id == answer_data.problem_id), None
        )

        if not hw_problem:
            raise domain_errors.BadRequestError("Problem not in this homework")

        # Get or create statistics
        stats = await self.stats_repo.get_or_create_stats(
            student.id, answer_data.homework_id, homework.max_score
        )

        # Check answer and calculate score
        is_correct = self._check_answer(answer_data.answer, problem.correct_answer)

        if is_correct:
            # Add points for this problem
            new_score = stats.score + hw_problem.points
            new_score = min(new_score, stats.max_score)  # Cap at max_score
        else:
            new_score = stats.score

        # Update statistics
        updated_stats = await self.stats_repo.update(
            stats.id,
            {
                "score": new_score,
                "status": "in_progress",
                "attempts_count": stats.attempts_count + 1,
                "time_spent_minutes": stats.time_spent_minutes + answer_data.time_spent_minutes,
            },
        )

        if not updated_stats:
            raise domain_errors.InternalError("Failed to update statistics")

        return homework_schemas.StatisticsResponse.model_validate(updated_stats)

    async def submit_homework(
        self,
        homework_id: int,
        student_user_id: int,
    ) -> homework_schemas.StatisticsResponse:
        """
        Submit homework for grading

        Args:
            homework_id: Homework ID
            student_user_id: User ID of student

        Returns:
            Final statistics
        """
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise domain_errors.ForbiddenError("Only students can submit homework")

        # Get statistics
        stats = await self.stats_repo.get_student_homework_stats(student.id, homework_id)
        if not stats:
            raise domain_errors.NotFoundError("No attempts found for this homework")

        # Mark as submitted
        updated_stats = await self.stats_repo.submit_homework(stats.id)
        if not updated_stats:
            raise domain_errors.InternalError("Failed to submit homework")

        return homework_schemas.StatisticsResponse.model_validate(updated_stats)

    def _check_answer(self, student_answer: str, correct_answer: str | None) -> bool:
        """
        Check if answer is correct

        Simple string comparison for now.
        Can be extended for different problem types.
        """
        if not correct_answer:
            return False  # Auto-graded only if correct_answer is set

        # Simple case-insensitive comparison
        return student_answer.strip().lower() == correct_answer.strip().lower()

    async def get_homework_status(
        self,
        homework_id: int,
        student_user_id: int,
    ) -> homework_schemas.StatisticsResponse:
        """
        Get current status/progress for homework

        Args:
            homework_id: Homework ID
            student_user_id: User ID of student

        Returns:
            Statistics including score, attempts, time spent

        Raises:
            DomainError: If student not found or no attempts found
        """
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise domain_errors.NotFoundError("Student not found")

        stats = await self.stats_repo.get_student_homework_stats(student.id, homework_id)
        if not stats:
            raise domain_errors.NotFoundError("No attempts found for this homework")

        return homework_schemas.StatisticsResponse.model_validate(stats)
