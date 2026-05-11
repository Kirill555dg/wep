"""
Classroom service
"""

import nanoid
from sqlalchemy.ext import asyncio as sa_asyncio

from app.domain import errors as domain_errors
from app.core import pagination as core_pagination
from app.repositories import classroom as classroom_repository
from app.repositories import user as user_repository
from app.schemas import communication as communication_schemas
from app.schemas import classrooms as classroom_schemas
from app.services import access_control as access_control


class ClassroomService:
    """
    Service for classroom management

    Handles classroom creation, invites, student enrollment
    """

    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.classroom_repo = classroom_repository.ClassroomRepository(db)
        self.student_classroom_repo = classroom_repository.StudentClassroomRepository(db)
        self.invite_repo = classroom_repository.InviteRepository(db)
        self.teacher_repo = user_repository.TeacherRepository(db)
        self.student_repo = user_repository.StudentRepository(db)

    async def create_classroom(
        self,
        classroom_data: classroom_schemas.ClassroomCreate,
        teacher_user_id: int,
    ) -> classroom_schemas.ClassroomResponse:
        """
        Create new classroom

        Args:
            classroom_data: Classroom creation data
            teacher_user_id: User ID of the teacher

        Returns:
            Created classroom

        Raises:
            HTTPException: If user is not a teacher
        """
        # Verify user is a teacher
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only teachers can create classrooms",
        )

        # Generate unique invite code
        invite_code = nanoid.generate(size=10)

        # Create classroom
        classroom = await self.classroom_repo.create(
            {**classroom_data.model_dump(), "teacher_id": teacher.id, "invite_code": invite_code}
        )

        response = classroom_schemas.ClassroomResponse.model_validate(classroom)
        response.students_count = 0
        return response

    async def get_classroom(self, classroom_id: int) -> classroom_schemas.ClassroomResponse:
        """Get classroom by ID"""
        classroom = await self.classroom_repo.get_by_id(classroom_id)
        if not classroom:
            raise domain_errors.NotFoundError("Classroom not found")

        response = classroom_schemas.ClassroomResponse.model_validate(classroom)
        response.students_count = await self.student_classroom_repo.count_students_in_classroom(
            classroom_id
        )
        return response

    async def get_teacher_classrooms(
        self,
        teacher_user_id: int,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[classroom_schemas.ClassroomResponse]:
        """Get classrooms for teacher"""
        teacher = await self.teacher_repo.get_by_user_id(teacher_user_id)
        if not teacher:
            return []

        classrooms = await self.classroom_repo.get_by_teacher(teacher.id, skip, limit)
        return [classroom_schemas.ClassroomResponse.model_validate(c) for c in classrooms]

    async def count_teacher_classrooms(self, teacher_user_id: int) -> int:
        teacher = await self.teacher_repo.get_by_user_id(teacher_user_id)
        if not teacher:
            return 0
        return await self.classroom_repo.count_by_teacher(teacher.id)

    async def get_student_classrooms(
        self,
        student_user_id: int,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[classroom_schemas.ClassroomResponse]:
        """Get classrooms for student"""
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return []

        memberships = await self.student_classroom_repo.get_by_student(student.id, skip, limit)
        classroom_ids = [m.classroom_id for m in memberships]

        classrooms = await self.classroom_repo.get_by_ids(classroom_ids)
        return [classroom_schemas.ClassroomResponse.model_validate(classroom_item) for classroom_item in classrooms]

    async def count_student_classrooms(self, student_user_id: int) -> int:
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            return 0
        return await self.student_classroom_repo.count_by_student(student.id)

    async def update_classroom(
        self,
        classroom_id: int,
        classroom_data: classroom_schemas.ClassroomUpdate,
        teacher_user_id: int,
    ) -> classroom_schemas.ClassroomResponse:
        """Update classroom (teacher only)"""
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(classroom_id),
            detail="Classroom not found",
        )

        # Verify teacher owns classroom
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only classroom owner can update it",
        )
        access_control.require_teacher_owns_classroom(
            teacher=teacher,
            classroom=classroom,
            detail="Only classroom owner can update it",
        )

        updated = await self.classroom_repo.update(
            classroom_id, classroom_data.model_dump(exclude_unset=True)
        )
        if not updated:
            raise domain_errors.InternalError("Failed to update classroom")

        return classroom_schemas.ClassroomResponse.model_validate(updated)

    async def join_classroom(
        self,
        join_data: classroom_schemas.JoinClassroomRequest,
        student_user_id: int,
    ) -> classroom_schemas.ClassroomResponse:
        """
        Student joins classroom via invite code

        Args:
            join_data: Invite code
            student_user_id: User ID of the student

        Returns:
            Joined classroom

        Raises:
            HTTPException: If invite invalid or user not a student
        """
        # Verify user is a student
        student = await self.student_repo.get_by_user_id(student_user_id)
        if not student:
            raise domain_errors.ForbiddenError("Only students can join classrooms")

        # Find classroom by invite code
        classroom = await self.classroom_repo.get_by_invite_code(join_data.invite_code)
        if not classroom:
            raise domain_errors.NotFoundError("Invalid invite code")

        # Check if already member
        existing = await self.student_classroom_repo.get_membership(student.id, classroom.id)
        if existing and existing.is_active:
            raise domain_errors.BadRequestError("Already a member of this classroom")

        # Check max students
        current_students = await self.student_classroom_repo.count_students_in_classroom(classroom.id)
        if classroom.max_students and current_students >= classroom.max_students:
            raise domain_errors.BadRequestError("Classroom is full")

        # Enroll student
        if existing:
            # Reactivate membership
            await self.student_classroom_repo.update(existing.id, {"is_active": True})
        else:
            # Create new membership
            await self.student_classroom_repo.create(
                {"student_id": student.id, "classroom_id": classroom.id}
            )

        return classroom_schemas.ClassroomResponse.model_validate(classroom)

    async def get_classroom_students(
        self,
        classroom_id: int,
        teacher_user_id: int,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[classroom_schemas.ClassroomStudentResponse]:
        """
        Get list of students in classroom (teacher only)

        Args:
            classroom_id: Classroom ID
            teacher_user_id: User ID of teacher (for verification)
            skip: Pagination offset
            limit: Pagination limit

        Returns:
            List of students with enrollment info

        Raises:
            HTTPException: If not authorized
        """
        # Verify teacher owns classroom
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(classroom_id),
            detail="Classroom not found",
        )
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only classroom owner can view students",
        )
        access_control.require_teacher_owns_classroom(
            teacher=teacher,
            classroom=classroom,
            detail="Only classroom owner can view students",
        )

        # Get students
        rows = await self.student_classroom_repo.get_students_with_user_by_classroom(
            classroom_id, skip, limit
        )

        students: list[classroom_schemas.ClassroomStudentResponse] = []
        for membership, student, user in rows:
            students.append(
                classroom_schemas.ClassroomStudentResponse(
                    student_id=int(student.id),
                    user=communication_schemas.UserPublic.model_validate(user),
                    enrolled_at=membership.enrolled_at,
                    grade_level=student.grade_level,
                )
            )

        return students

    async def count_classroom_students(self, classroom_id: int, teacher_user_id: int) -> int:
        classroom = access_control.require_classroom(
            await self.classroom_repo.get_by_id(classroom_id),
            detail="Classroom not found",
        )
        teacher = access_control.require_teacher_profile(
            await self.teacher_repo.get_by_user_id(teacher_user_id),
            detail="Only classroom owner can view students",
        )
        access_control.require_teacher_owns_classroom(
            teacher=teacher,
            classroom=classroom,
            detail="Only classroom owner can view students",
        )
        return await self.student_classroom_repo.count_students_in_classroom(classroom_id)
