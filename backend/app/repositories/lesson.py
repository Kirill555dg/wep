"""
Lesson and Theory Material repositories
"""

import typing as tp

import sqlalchemy as sa
from sqlalchemy import orm as orm
from sqlalchemy.ext import asyncio as sa_asyncio

from app.models import lessons as lesson_models
from app.models import theory as theory_models
from app.repositories import base as base_repository


class LessonRepository(base_repository.BaseRepository[lesson_models.Lesson]):
    """Repository for Lesson operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(lesson_models.Lesson, db)

    async def get_by_classroom(
        self, classroom_id: int, skip: int = 0, limit: int = 100
    ) -> list[lesson_models.Lesson]:
        """Get lessons for classroom"""
        stmt = (
            sa.select(lesson_models.Lesson)
            .where(lesson_models.Lesson.classroom_id == classroom_id)
            .order_by(lesson_models.Lesson.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[lesson_models.Lesson], items)

    async def get_published(
        self, classroom_id: int, skip: int = 0, limit: int = 100
    ) -> list[lesson_models.Lesson]:
        """Get published lessons for classroom"""
        stmt = (
            sa.select(lesson_models.Lesson)
            .where(
                lesson_models.Lesson.classroom_id == classroom_id,
                lesson_models.Lesson.is_published,
            )
            .order_by(lesson_models.Lesson.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[lesson_models.Lesson], items)

    async def get_with_materials(self, lesson_id: int) -> lesson_models.Lesson | None:
        """Get lesson with materials"""
        stmt = (
            sa.select(lesson_models.Lesson)
            .options(orm.joinedload(lesson_models.Lesson.lesson_materials))
            .where(lesson_models.Lesson.id == lesson_id)
        )
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(lesson_models.Lesson | None, obj)

    async def count_by_classroom(self, classroom_id: int) -> int:
        """Count lessons in classroom"""
        stmt = (
            sa.select(sa.func.count())
            .select_from(lesson_models.Lesson)
            .where(lesson_models.Lesson.classroom_id == classroom_id)
        )
        result = await self.db.execute(stmt)
        count_value = result.scalar_one()
        return tp.cast(int, count_value)

    async def count_published_by_classroom(self, classroom_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(lesson_models.Lesson)
            .where(
                lesson_models.Lesson.classroom_id == classroom_id,
                lesson_models.Lesson.is_published,
            )
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)


class LessonMaterialRepository(base_repository.BaseRepository[lesson_models.LessonMaterial]):
    """Repository for LessonMaterial operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(lesson_models.LessonMaterial, db)

    async def get_by_lesson(self, lesson_id: int) -> list[lesson_models.LessonMaterial]:
        """Get materials for lesson"""
        stmt = (
            sa.select(lesson_models.LessonMaterial)
            .where(lesson_models.LessonMaterial.lesson_id == lesson_id)
            .order_by(lesson_models.LessonMaterial.order_number)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[lesson_models.LessonMaterial], items)

    async def add_material_to_lesson(
        self, lesson_id: int, material_id: int, order_number: int = 0, is_required: bool = True
    ) -> lesson_models.LessonMaterial:
        """Add material to lesson"""
        return await self.create(
            {
                "lesson_id": lesson_id,
                "theory_material_id": material_id,
                "order_number": order_number,
                "is_required": is_required,
            }
        )


class TheoryMaterialRepository(base_repository.BaseRepository[theory_models.TheoryMaterial]):
    """Repository for TheoryMaterial operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(theory_models.TheoryMaterial, db)

    async def get_by_subsection(
        self, subsection_id: int, skip: int = 0, limit: int = 100
    ) -> list[theory_models.TheoryMaterial]:
        """Get materials for subsection"""
        stmt = (
            sa.select(theory_models.TheoryMaterial)
            .where(theory_models.TheoryMaterial.subsection_id == subsection_id)
            .order_by(theory_models.TheoryMaterial.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[theory_models.TheoryMaterial], items)

    async def get_published(
        self, subsection_id: int, skip: int = 0, limit: int = 100
    ) -> list[theory_models.TheoryMaterial]:
        """Get published materials for subsection"""
        stmt = (
            sa.select(theory_models.TheoryMaterial)
            .where(
                theory_models.TheoryMaterial.subsection_id == subsection_id,
                theory_models.TheoryMaterial.is_published,
            )
            .order_by(theory_models.TheoryMaterial.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[theory_models.TheoryMaterial], items)

    async def count_by_subsection(self, subsection_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(theory_models.TheoryMaterial)
            .where(theory_models.TheoryMaterial.subsection_id == subsection_id)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)

    async def count_published_by_subsection(self, subsection_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(theory_models.TheoryMaterial)
            .where(
                theory_models.TheoryMaterial.subsection_id == subsection_id,
                theory_models.TheoryMaterial.is_published,
            )
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)


class SubjectRepository(base_repository.BaseRepository[theory_models.Subject]):
    """Repository for Subject operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(theory_models.Subject, db)

    async def get_by_name(self, name: str) -> theory_models.Subject | None:
        """Get subject by name"""
        stmt = sa.select(theory_models.Subject).where(theory_models.Subject.name == name)
        obj = await self._scalar_one_or_none(stmt)
        return tp.cast(theory_models.Subject | None, obj)

    async def get_active(self, skip: int = 0, limit: int = 100) -> list[theory_models.Subject]:
        """Get active subjects"""
        stmt = (
            sa.select(theory_models.Subject)
            .where(theory_models.Subject.is_active)
            .order_by(theory_models.Subject.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[theory_models.Subject], items)

    async def count_active(self) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(theory_models.Subject)
            .where(theory_models.Subject.is_active)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)


class SectionRepository(base_repository.BaseRepository[theory_models.Section]):
    """Repository for Section operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(theory_models.Section, db)

    async def get_by_subject(
        self, subject_id: int, skip: int = 0, limit: int = 100
    ) -> list[theory_models.Section]:
        stmt = (
            sa.select(theory_models.Section)
            .where(theory_models.Section.subject_id == subject_id)
            .order_by(theory_models.Section.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[theory_models.Section], items)

    async def count_by_subject(self, subject_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(theory_models.Section)
            .where(theory_models.Section.subject_id == subject_id)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)


class SubsectionRepository(base_repository.BaseRepository[theory_models.Subsection]):
    """Repository for Subsection operations"""

    def __init__(self, db: sa_asyncio.AsyncSession):
        super().__init__(theory_models.Subsection, db)

    async def get_by_section(
        self, section_id: int, skip: int = 0, limit: int = 100
    ) -> list[theory_models.Subsection]:
        stmt = (
            sa.select(theory_models.Subsection)
            .where(theory_models.Subsection.section_id == section_id)
            .order_by(theory_models.Subsection.order_number)
            .offset(skip)
            .limit(limit)
        )
        items = await self._scalars_all(stmt)
        return tp.cast(list[theory_models.Subsection], items)

    async def count_by_section(self, section_id: int) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(theory_models.Subsection)
            .where(theory_models.Subsection.section_id == section_id)
        )
        value = (await self.db.execute(stmt)).scalar_one()
        return tp.cast(int, value)
