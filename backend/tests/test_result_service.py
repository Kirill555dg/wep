"""
Tests for ResultService aggregations.
"""

import pytest

from app.models import homework as homework_models
from app.repositories import classroom as classroom_repo
from app.repositories import homework as homework_repo
from app.services import auth as auth_service_module
from app.services import classroom as classroom_service_module
from app.services import lesson as lesson_service_module
from app.services import result as result_service_module
from app.schemas import classrooms as classroom_schemas
from app.schemas import lessons as lesson_schemas
from app.schemas import users as user_schemas


pytestmark = pytest.mark.anyio


async def test_result_service_classroom_progress_aggregates(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    classroom_service = classroom_service_module.ClassroomService(db_session)
    lesson_service = lesson_service_module.LessonService(db_session)
    result_service = result_service_module.ResultService(db_session)

    teacher = await auth_service.register_user(
        user_schemas.UserCreate(
            email="teacher_progress@example.com",
            password="TestPassword123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )
    student = await auth_service.register_user(
        user_schemas.UserCreate(
            email="student_progress@example.com",
            password="StudentPass456!",
            first_name="Stud",
            last_name="Ent",
            role="student",
        )
    )

    created_classroom = await classroom_service.create_classroom(
        classroom_schemas.ClassroomCreate(
            name="Progress class",
            subject="Math",
            grade_level=7,
        ),
        teacher.id,
    )

    # Student joins classroom, to create membership (student_id is Student.id)
    await classroom_service.join_classroom(
        classroom_schemas.JoinClassroomRequest(invite_code=created_classroom.invite_code),  # type: ignore[arg-type]
        student.id,
    )

    lesson = await lesson_service.create_lesson(
        lesson_schemas.LessonCreate(
            classroom_id=created_classroom.id,
            title="Lesson 1",
            description="...",
            theory_material_ids=[],
        ),
        teacher.id,
    )

    # Create two homeworks in DB directly via repository.
    homework_repository = homework_repo.HomeworkRepository(db_session)
    homework1 = await homework_repository.create(
        {"lesson_id": lesson.id, "title": "HW1", "description": "", "max_score": 100.0, "is_published": True}
    )
    homework2 = await homework_repository.create(
        {"lesson_id": lesson.id, "title": "HW2", "description": "", "max_score": 100.0, "is_published": True}
    )

    # Resolve internal student_id (Student.id) via membership records.
    membership_repository = classroom_repo.StudentClassroomRepository(db_session)
    memberships = await membership_repository.get_by_classroom(created_classroom.id)
    assert len(memberships) == 1
    student_id = memberships[0].student_id

    stats_repository = homework_repo.StatisticsRepository(db_session)
    await stats_repository.create(
        {
            "student_id": student_id,
            "homework_id": homework1.id,
            "max_score": 100.0,
            "score": 0.0,
            "status": homework_models.HomeworkStatus.GRADED,
            "attempts_count": 1,
            "time_spent_minutes": 10,
        }
    )
    await stats_repository.create(
        {
            "student_id": student_id,
            "homework_id": homework2.id,
            "max_score": 100.0,
            "score": 0.0,
            "status": homework_models.HomeworkStatus.NOT_STARTED,
            "attempts_count": 0,
            "time_spent_minutes": 0,
        }
    )

    progress = await result_service.get_classroom_progress(created_classroom.id, teacher.id)
    assert progress.total_students == 1
    assert progress.total_homeworks_assigned == 2
    assert progress.completed_homeworks == 1
    assert progress.average_completion_rate == 50.0


async def test_result_service_student_progress_aggregates(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    classroom_service = classroom_service_module.ClassroomService(db_session)
    lesson_service = lesson_service_module.LessonService(db_session)
    result_service = result_service_module.ResultService(db_session)

    teacher = await auth_service.register_user(
        user_schemas.UserCreate(
            email="teacher_summary@example.com",
            password="TestPassword123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )
    student = await auth_service.register_user(
        user_schemas.UserCreate(
            email="student_summary@example.com",
            password="StudentPass456!",
            first_name="Stud",
            last_name="Ent",
            role="student",
        )
    )

    student_record = await result_service.student_repo.get_by_user_id(student.id)
    assert student_record is not None

    stats_repository = homework_repo.StatisticsRepository(db_session)

    created_classroom = await classroom_service.create_classroom(
        classroom_schemas.ClassroomCreate(
            name="Progress class 2",
            subject="Math",
            grade_level=7,
        ),
        teacher.id,
    )
    lesson = await lesson_service.create_lesson(
        lesson_schemas.LessonCreate(
            classroom_id=created_classroom.id,
            title="Lesson 1",
            description="...",
            theory_material_ids=[],
        ),
        teacher.id,
    )

    homework_repository = homework_repo.HomeworkRepository(db_session)
    homework1 = await homework_repository.create(
        {"lesson_id": lesson.id, "title": "HW1", "description": "", "max_score": 100.0, "is_published": True}
    )
    homework2 = await homework_repository.create(
        {"lesson_id": lesson.id, "title": "HW2", "description": "", "max_score": 100.0, "is_published": True}
    )
    homework3 = await homework_repository.create(
        {"lesson_id": lesson.id, "title": "HW3", "description": "", "max_score": 100.0, "is_published": True}
    )

    # Create 3 stats rows directly to test aggregation.
    await stats_repository.create(
        {
            "student_id": student_record.id,
            "homework_id": homework1.id,
            "max_score": 100.0,
            "score": 80.0,
            "status": homework_models.HomeworkStatus.GRADED,
            "attempts_count": 1,
            "time_spent_minutes": 10,
        }
    )
    await stats_repository.create(
        {
            "student_id": student_record.id,
            "homework_id": homework2.id,
            "max_score": 100.0,
            "score": 0.0,
            "status": homework_models.HomeworkStatus.SUBMITTED,
            "attempts_count": 1,
            "time_spent_minutes": 5,
        }
    )
    await stats_repository.create(
        {
            "student_id": student_record.id,
            "homework_id": homework3.id,
            "max_score": 100.0,
            "score": 0.0,
            "status": homework_models.HomeworkStatus.IN_PROGRESS,
            "attempts_count": 2,
            "time_spent_minutes": 20,
        }
    )

    summary = await result_service.get_student_progress(student.id)
    assert summary.total_homeworks == 3
    assert summary.completed == 2
    assert summary.in_progress == 1
    assert summary.not_started == 0
    assert summary.total_attempts == 4
    assert summary.total_time_spent_minutes == 35
    assert summary.average_score_percentage == 80.0

