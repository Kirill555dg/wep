"""
Tests for TheoryService.
"""

import pytest

from app.models import theory as theory_models
from app.repositories import user as user_repository
from app.services import auth as auth_service_module
from app.services import theory as theory_service_module
from app.schemas import users as user_schemas


pytestmark = pytest.mark.anyio


async def test_theory_service_filters_unpublished_for_students(db_session):
    auth_service = auth_service_module.AuthService(db_session)
    theory_service = theory_service_module.TheoryService(db_session)
    user_repo = user_repository.UserRepository(db_session)

    teacher_user = await auth_service.register_user(
        user_schemas.UserCreate(
            email="theory_teacher@example.com",
            password="TeacherPass123!",
            first_name="Teach",
            last_name="Er",
            role="teacher",
        )
    )
    student_user = await auth_service.register_user(
        user_schemas.UserCreate(
            email="theory_student@example.com",
            password="StudentPass123!",
            first_name="Stud",
            last_name="Ent",
            role="student",
        )
    )

    teacher = await user_repo.get_by_id(teacher_user.id)
    student = await user_repo.get_by_id(student_user.id)
    assert teacher is not None and student is not None

    subject = theory_models.Subject(name="S1", description=None, icon_url=None, order_number=1, is_active=True)
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)

    section = theory_models.Section(subject_id=subject.id, name="Sec", description=None, order_number=1)
    db_session.add(section)
    await db_session.commit()
    await db_session.refresh(section)

    subsection = theory_models.Subsection(section_id=section.id, name="Sub", description=None, order_number=1)
    db_session.add(subsection)
    await db_session.commit()
    await db_session.refresh(subsection)

    published = theory_models.TheoryMaterial(
        subsection_id=subsection.id,
        title="P",
        content="published",
        order_number=1,
        estimated_read_time=1,
        is_published=True,
    )
    hidden = theory_models.TheoryMaterial(
        subsection_id=subsection.id,
        title="H",
        content="hidden",
        order_number=2,
        estimated_read_time=1,
        is_published=False,
    )
    db_session.add_all([published, hidden])
    await db_session.commit()

    student_items = await theory_service.list_materials(subsection.id, user=student, skip=0, limit=100)
    assert [m.title for m in student_items] == ["P"]

    teacher_items = await theory_service.list_materials(subsection.id, user=teacher, skip=0, limit=100)
    assert [m.title for m in teacher_items] == ["P", "H"]

