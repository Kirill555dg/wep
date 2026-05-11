"""
Homework service
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.domain import errors as domain_errors
from app.core import pagination as core_pagination
from app.models import users as user_models
from app.repositories import classroom as classroom_repository
from app.repositories import homework as homework_repository
from app.repositories import lesson as lesson_repository
from app.repositories import user as user_repository
from app.schemas import homework as homework_schemas
from app.services import access_control as access_control


class HomeworkService:
    """
    Service for homework management

    Handles homework creation, problem assignment, viewing
    """

    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.homework_repo = homework_repository.HomeworkRepository(db)
        self.hw_problem_repo = homework_repository.HomeworkProblemRepository(db)
        self.problem_repo = homework_repository.ProblemRepository(db)
        self.lesson_repo = lesson_repository.LessonRepository(db)
        self.classroom_repo = classroom_repository.ClassroomRepository(db)
        self.teacher_repo = user_repository.TeacherRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def create_homework(
        self,
        homework_data: homework_schemas.HomeworkCreate,
        teacher_user_id: int,
    ) -> homework_schemas.HomeworkResponse:
        """
        Create new homework

        Args:
            homework_data: Homework creation data
            teacher_user_id: User ID of teacher

        Returns:
            Created homework

        Raises:
            DomainError: If not authorized
        """
        # Verify lesson exists
        lesson = await self.lesson_repo.get_by_id(homework_data.lesson_id)
        if not lesson:
            raise domain_errors.NotFoundError("Lesson not found")

        # Verify teacher owns classroom
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(lesson.classroom_id),
            detail="Classroom not found",
        )
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only classroom owner can create homework",
        )
        access_control.require_teacher_owns_classroom(
            teacher=teacher,
            classroom=classroom,
            detail="Only classroom owner can create homework",
        )

        # Create homework
        homework_dict = homework_data.model_dump(exclude={"problem_ids", "problem_points"})
        homework = await self.homework_repo.create(homework_dict)

        # Add problems
        points_list = homework_data.problem_points or []
        for idx, problem_id in enumerate(homework_data.problem_ids):
            points = points_list[idx] if idx < len(points_list) else 10.0
            await self.hw_problem_repo.add_problem_to_homework(
                homework.id, problem_id, points=points, order_number=idx
            )

        response = homework_schemas.HomeworkResponse.model_validate(homework)
        response.problems_count = len(homework_data.problem_ids)
        return response

    async def get_homework(
        self, homework_id: int, user: user_models.User
    ) -> homework_schemas.HomeworkDetailResponse:
        """
        Get homework by ID

        Args:
            homework_id: Homework ID
            user_id: User ID (for permission check)

        Returns:
            Homework data
        """
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise domain_errors.NotFoundError("Homework not found")

        # Check if published for students
        lesson = await self.lesson_repo.get_by_id(homework.lesson_id)
        if not lesson:
            raise domain_errors.NotFoundError("Lesson not found")

        classroom = await self.classroom_repo.get_by_id(lesson.classroom_id)
        teacher = await self.teacher_repo.get_by_user_id(user.id) if user.role == "teacher" else None

        # If not teacher of this classroom and homework not published, deny access
        is_teacher = teacher and classroom and classroom.teacher_id == teacher.id
        if not is_teacher and not homework.is_published:
            raise domain_errors.ForbiddenError("Homework not published yet")

        response = homework_schemas.HomeworkDetailResponse.model_validate(homework)
        response.problems_count = len(await self.hw_problem_repo.get_by_homework(homework_id))
        return response

    async def get_homework_problems(
        self, homework_id: int, user: user_models.User
    ) -> list[homework_schemas.ProblemResponse | homework_schemas.ProblemFullResponse]:
        """
        Get problems for homework

        Teachers get full info (with answers), students get limited info
        """
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise domain_errors.NotFoundError("Homework not found")

        lesson = await self.lesson_repo.get_by_id(homework.lesson_id)
        if not lesson:
            raise domain_errors.NotFoundError("Lesson not found")

        classroom = await self.classroom_repo.get_by_id(lesson.classroom_id)
        teacher = await self.teacher_repo.get_by_user_id(user.id) if user.role == "teacher" else None
        is_teacher = teacher and classroom and classroom.teacher_id == teacher.id

        # Get homework problems
        hw_problems = await self.hw_problem_repo.get_by_homework(homework_id)
        problem_ids = [hp.problem_id for hp in hw_problems]

        problems = await self.problem_repo.get_by_ids(problem_ids)
        problems_by_id = {problem_item.id: problem_item for problem_item in problems}
        problems_filtered = [problems_by_id[problem_id] for problem_id in problem_ids if problem_id in problems_by_id]

        if is_teacher:
            # Teachers see full info
            return [homework_schemas.ProblemFullResponse.model_validate(p) for p in problems_filtered]
        else:
            # Students don't see correct answers
            return [homework_schemas.ProblemResponse.model_validate(p) for p in problems_filtered]

    async def update_homework(
        self,
        homework_id: int,
        homework_data: homework_schemas.HomeworkUpdate,
        teacher_user_id: int,
    ) -> homework_schemas.HomeworkResponse:
        """Update homework (teacher only)"""
        homework = await self.homework_repo.get_by_id(homework_id)
        if not homework:
            raise domain_errors.NotFoundError("Homework not found")

        # Verify teacher owns classroom
        lesson = await self.lesson_repo.get_by_id(homework.lesson_id)
        if not lesson:
            raise domain_errors.NotFoundError("Lesson not found")

        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(lesson.classroom_id),
            detail="Classroom not found",
        )
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only classroom owner can update homework",
        )
        access_control.require_teacher_owns_classroom(
            teacher=teacher,
            classroom=classroom,
            detail="Only classroom owner can update homework",
        )

        updated = await self.homework_repo.update(
            homework_id, homework_data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise domain_errors.InternalError("Failed to update homework")

        return homework_schemas.HomeworkResponse.model_validate(updated)

    async def get_lesson_homework(
        self,
        lesson_id: int,
        user: user_models.User,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[homework_schemas.HomeworkResponse]:
        """
        Get all homework for a lesson

        Teachers see all homework (including unpublished), students see only published.

        Args:
            lesson_id: Lesson ID
            user_id: User ID (for permission check)
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of homework for the lesson
        """
        # Check if user is teacher of this lesson's classroom
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            return []

        teacher = await self.teacher_repo.get_by_user_id(user.id) if user.role == "teacher" else None
        classroom = await self.classroom_repo.get_by_id(lesson.classroom_id)
        is_teacher = teacher and classroom and classroom.teacher_id == teacher.id

        if is_teacher:
            # Teacher sees all homework
            homeworks = await self.homework_repo.get_by_lesson(lesson_id, skip, limit)
        else:
            # Students see only published
            homeworks = await self.homework_repo.get_published(lesson_id, skip, limit)

        return [homework_schemas.HomeworkResponse.model_validate(hw) for hw in homeworks]

    async def count_lesson_homework(self, lesson_id: int, user: user_models.User) -> int:
        lesson = await self.lesson_repo.get_by_id(lesson_id)
        if not lesson:
            return 0

        teacher = await self.teacher_repo.get_by_user_id(user.id) if user.role == "teacher" else None
        classroom = await self.classroom_repo.get_by_id(lesson.classroom_id)
        is_teacher = teacher and classroom and classroom.teacher_id == teacher.id
        if is_teacher:
            return await self.homework_repo.count_by_lesson(lesson_id)
        return await self.homework_repo.count_published_by_lesson(lesson_id)
