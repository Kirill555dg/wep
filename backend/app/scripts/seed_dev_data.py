"""
Seed development data into the database.

Creates:
- 1 teacher
- 2 classrooms
- 10 students (5 per classroom)
- subjects/sections/subsections/theory materials
- lessons, homeworks, problems, homework assignments
- statistics and basic classroom chats/messages

Run:
  python -m app.scripts.seed_dev_data
"""

import asyncio
import logging
import random

import sqlalchemy as sa
from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import logging_config as logging_config
from app.db import session as db_session
from app.models import communication as communication_models
from app.models import homework as homework_models
from app.models import problems as problem_models
from app.models import theory as theory_models
from app.models import users as user_models
from app.repositories import homework as homework_repo
from app.repositories import lesson as lesson_repo
from app.repositories import user as user_repo
from app.schemas import classrooms as classroom_schemas
from app.schemas import homework as homework_schemas
from app.schemas import lessons as lesson_schemas
from app.schemas import users as user_schemas
from app.services import auth as auth_service_module
from app.services import classroom as classroom_service_module
from app.services import homework as homework_service_module
from app.services import lesson as lesson_service_module
from app.services import problem as problem_service_module


logger = logging.getLogger("app.seed")


async def _exists_any_user(session: sa_asyncio.AsyncSession) -> bool:
    stmt = sa.select(sa.func.count()).select_from(user_models.User)
    count_value = (await session.execute(stmt)).scalar_one()
    return int(count_value) > 0


async def _ensure_math_taxonomy(session: sa_asyncio.AsyncSession) -> int:
    """
    Ensure Subject/Section/Subsection exist, return subsection_id.
    """
    subject_repo = lesson_repo.SubjectRepository(session)
    subject = await subject_repo.get_by_name("Mathematics")
    if subject is None:
        subject = await subject_repo.create(
            {
                "name": "Mathematics",
                "description": "Demo subject for seeded data",
                "order_number": 1,
                "is_active": True,
            }
        )

    # Section/Subsection repositories are not present; create via ORM for now.
    section = (
        await session.execute(
            sa.select(theory_models.Section).where(
                theory_models.Section.subject_id == subject.id,
                theory_models.Section.name == "Algebra",
            )
        )
    ).scalar_one_or_none()
    if section is None:
        section = theory_models.Section(
            subject_id=subject.id,
            name="Algebra",
            description="Algebra basics",
            order_number=1,
        )
        session.add(section)
        await session.commit()
        await session.refresh(section)

    subsection = (
        await session.execute(
            sa.select(theory_models.Subsection).where(
                theory_models.Subsection.section_id == section.id,
                theory_models.Subsection.name == "Linear equations",
            )
        )
    ).scalar_one_or_none()
    if subsection is None:
        subsection = theory_models.Subsection(
            section_id=section.id,
            name="Linear equations",
            description="One-variable linear equations",
            order_number=1,
        )
        session.add(subsection)
        await session.commit()
        await session.refresh(subsection)

    return int(subsection.id)


async def seed_dev_data() -> None:
    logging_config.setup_logging()
    random.seed(0)

    async with db_session.AsyncSessionLocal() as session:
        # Safety guard: this script is meant for an empty dev DB.
        if await _exists_any_user(session):
            logger.warning("seed_skipped_db_not_empty")
            return

        auth_service = auth_service_module.AuthService(session)
        classroom_service = classroom_service_module.ClassroomService(session)
        lesson_service = lesson_service_module.LessonService(session)
        homework_service = homework_service_module.HomeworkService(session)
        problem_service = problem_service_module.ProblemService(homework_repo.ProblemRepository(session))

        teacher = await auth_service.register_user(
            user_schemas.UserCreate(
                email="teacher@wep.dev",
                password="TeacherPass123!",
                first_name="Alex",
                last_name="Teacher",
                middle_name="A",
                role="teacher",
            )
        )

        logger.info("seed_teacher_created", extra={"teacher_user_id": teacher.id, "email": teacher.email})

        classroom_a = await classroom_service.create_classroom(
            classroom_schemas.ClassroomCreate(
                name="7A Mathematics",
                subject="Math",
                grade_level=7,
                description="Seeded classroom A",
            ),
            teacher.id,
        )
        classroom_b = await classroom_service.create_classroom(
            classroom_schemas.ClassroomCreate(
                name="7B Mathematics",
                subject="Math",
                grade_level=7,
                description="Seeded classroom B",
            ),
            teacher.id,
        )

        if classroom_a.invite_code is None or classroom_b.invite_code is None:
            raise RuntimeError("Expected invite codes to be generated for seeded classrooms")

        logger.info(
            "seed_classrooms_created",
            extra={
                "classroom_a_id": classroom_a.id,
                "classroom_b_id": classroom_b.id,
                "invite_a": classroom_a.invite_code,
                "invite_b": classroom_b.invite_code,
            },
        )

        students: list[user_schemas.UserResponse] = []
        for idx in range(1, 11):
            student = await auth_service.register_user(
                user_schemas.UserCreate(
                    email=f"student{idx}@wep.dev",
                    password="StudentPass123!",
                    first_name=f"Student{idx}",
                    last_name="Demo",
                    role="student",
                )
            )
            students.append(student)

        logger.info("seed_students_created", extra={"count": len(students)})

        # Enroll 5 students per classroom.
        for student in students[:5]:
            await classroom_service.join_classroom(
                classroom_schemas.JoinClassroomRequest(invite_code=classroom_a.invite_code),
                student.id,
            )
        for student in students[5:]:
            await classroom_service.join_classroom(
                classroom_schemas.JoinClassroomRequest(invite_code=classroom_b.invite_code),
                student.id,
            )

        # Create taxonomy and theory materials
        subsection_id = await _ensure_math_taxonomy(session)
        theory_repo = lesson_repo.TheoryMaterialRepository(session)
        materials: list[theory_models.TheoryMaterial] = []
        for idx in range(1, 7):
            material = await theory_repo.create(
                {
                    "subsection_id": subsection_id,
                    "title": f"Linear equations — part {idx}",
                    "content": f"# Linear equations (part {idx})\\n\\nSeeded material for development.",
                    "order_number": idx,
                    "estimated_read_time": 5,
                    "is_published": True,
                }
            )
            materials.append(material)

        # Lessons: 2 per classroom, each attaches 3 materials.
        async def create_lesson_bundle(classroom_id: int, *, title_prefix: str) -> list[int]:
            lesson_ids: list[int] = []
            for lesson_idx in range(1, 3):
                material_ids = [materials[(lesson_idx - 1) * 3 + i].id for i in range(3)]
                lesson = await lesson_service.create_lesson(
                    lesson_schemas.LessonCreate(
                        classroom_id=classroom_id,
                        title=f"{title_prefix} Lesson {lesson_idx}",
                        description="Seeded lesson",
                        theory_material_ids=[int(x) for x in material_ids],
                    ),
                    teacher.id,
                )
                # Publish lesson
                await lesson_repo.LessonRepository(session).update(lesson.id, {"is_published": True})
                lesson_ids.append(int(lesson.id))
            return lesson_ids

        lesson_ids_a = await create_lesson_bundle(classroom_a.id, title_prefix="7A")
        lesson_ids_b = await create_lesson_bundle(classroom_b.id, title_prefix="7B")

        # Problems: create a small pool and publish them.
        problems: list[problem_models.Problem] = []
        for idx in range(1, 11):
            problem = await problem_service.create_problem(
                homework_schemas.ProblemCreate(
                    title=f"Equation problem {idx}",
                    description=f"Solve x + {idx} = {idx * 2}.",
                    problem_type="text",
                    difficulty=1,
                    correct_answer=str(idx),
                    explanation="Move constants to the other side.",
                    hints="Try isolating x.",
                ),
                teacher_id=teacher.id,
            )
            # Publish problem
            await homework_repo.ProblemRepository(session).update(problem.id, {"is_published": True})
            problems.append(problem)

        # Homeworks: 2 per classroom (one per lesson), assign 5 problems.
        async def create_homeworks_for_lessons(lesson_ids: list[int]) -> list[int]:
            hw_ids: list[int] = []
            for i, lesson_id in enumerate(lesson_ids, start=1):
                problem_slice = problems[(i - 1) * 5 : i * 5]
                homework = await homework_service.create_homework(
                    homework_schemas.HomeworkCreate(
                        lesson_id=lesson_id,
                        title=f"Homework {i}",
                        description="Seeded homework",
                        max_score=50.0,
                        problem_ids=[int(p.id) for p in problem_slice],
                        problem_points=[10.0] * len(problem_slice),
                    ),
                    teacher.id,
                )
                await homework_repo.HomeworkRepository(session).update(homework.id, {"is_published": True})
                hw_ids.append(int(homework.id))
            return hw_ids

        homework_ids_a = await create_homeworks_for_lessons(lesson_ids_a)
        homework_ids_b = await create_homeworks_for_lessons(lesson_ids_b)

        # Create chats (1 per classroom) and a couple of messages.
        chats: dict[int, int] = {}
        for classroom in (classroom_a, classroom_b):
            chat = communication_models.Chat(classroom_id=classroom.id, name=f"{classroom.name} chat")
            session.add(chat)
            await session.commit()
            await session.refresh(chat)
            chats[classroom.id] = int(chat.id)

        # Messages (teacher + first student in each class)
        for classroom, student in ((classroom_a, students[0]), (classroom_b, students[5])):
            chat_id = chats[classroom.id]
            session.add(
                communication_models.Message(
                    chat_id=chat_id,
                    sender_id=teacher.id,
                    content=f"Welcome to {classroom.name}!",
                )
            )
            session.add(
                communication_models.Message(
                    chat_id=chat_id,
                    sender_id=student.id,
                    content="Hello! Ready to learn.",
                )
            )
            await session.commit()

        # Statistics: create per student per homework with mixed statuses.
        stats_repo = homework_repo.StatisticsRepository(session)
        student_repo = user_repo.StudentRepository(session)

        async def seed_stats(student_user_ids: list[int], homework_ids: list[int]) -> None:
            for user_id in student_user_ids:
                student = await student_repo.get_by_user_id(user_id)
                if student is None:
                    continue
                for hw_id in homework_ids:
                    status = random.choice(
                        [
                            homework_models.HomeworkStatus.NOT_STARTED,
                            homework_models.HomeworkStatus.IN_PROGRESS,
                            homework_models.HomeworkStatus.SUBMITTED,
                            homework_models.HomeworkStatus.GRADED,
                        ]
                    )
                    score = 0.0
                    attempts = 0
                    if status in (homework_models.HomeworkStatus.SUBMITTED, homework_models.HomeworkStatus.GRADED):
                        score = float(random.choice([30.0, 40.0, 50.0]))
                        attempts = int(random.choice([1, 2, 3]))
                    elif status == homework_models.HomeworkStatus.IN_PROGRESS:
                        score = float(random.choice([10.0, 20.0, 30.0]))
                        attempts = int(random.choice([1, 2]))

                    await stats_repo.create(
                        {
                            "student_id": int(student.id),
                            "homework_id": hw_id,
                            "status": status,
                            "score": score,
                            "max_score": 50.0,
                            "attempts_count": attempts,
                            "time_spent_minutes": int(random.choice([0, 5, 10, 15, 20])),
                        }
                    )

        await seed_stats([s.id for s in students[:5]], homework_ids_a)
        await seed_stats([s.id for s in students[5:]], homework_ids_b)

        logger.info(
            "seed_done",
            extra={
                "teacher_email": teacher.email,
                "classrooms": [classroom_a.id, classroom_b.id],
                "students": len(students),
                "materials": len(materials),
                "problems": len(problems),
            },
        )


def main() -> None:
    asyncio.run(seed_dev_data())


if __name__ == "__main__":
    main()

