"""
Theory content service.
"""

from sqlalchemy.ext import asyncio as sa_asyncio

from app.core import pagination as core_pagination
from app.domain import errors as domain_errors
from app.models import users as user_models
from app.repositories import lesson as lesson_repository
from app.schemas import theory as theory_schemas


class TheoryService:
    def __init__(self, db: sa_asyncio.AsyncSession):
        self.db = db
        self.subject_repo = lesson_repository.SubjectRepository(db)
        self.section_repo = lesson_repository.SectionRepository(db)
        self.subsection_repo = lesson_repository.SubsectionRepository(db)
        self.material_repo = lesson_repository.TheoryMaterialRepository(db)

    async def list_subjects(
        self,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[theory_schemas.SubjectResponse]:
        subjects = await self.subject_repo.get_active(skip=skip, limit=limit)
        return [theory_schemas.SubjectResponse.model_validate(s) for s in subjects]

    async def count_subjects(self) -> int:
        return await self.subject_repo.count_active()

    async def get_subject(self, subject_id: int) -> theory_schemas.SubjectResponse:
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject:
            raise domain_errors.NotFoundError("Subject not found")
        return theory_schemas.SubjectResponse.model_validate(subject)

    async def list_sections(
        self,
        subject_id: int,
        *,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[theory_schemas.SectionResponse]:
        # Ensure subject exists
        if not await self.subject_repo.get_by_id(subject_id):
            raise domain_errors.NotFoundError("Subject not found")
        sections = await self.section_repo.get_by_subject(subject_id, skip=skip, limit=limit)
        return [theory_schemas.SectionResponse.model_validate(s) for s in sections]

    async def count_sections(self, subject_id: int) -> int:
        if not await self.subject_repo.get_by_id(subject_id):
            raise domain_errors.NotFoundError("Subject not found")
        return await self.section_repo.count_by_subject(subject_id)

    async def list_subsections(
        self,
        section_id: int,
        *,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[theory_schemas.SubsectionResponse]:
        if not await self.section_repo.get_by_id(section_id):
            raise domain_errors.NotFoundError("Section not found")
        subsections = await self.subsection_repo.get_by_section(section_id, skip=skip, limit=limit)
        return [theory_schemas.SubsectionResponse.model_validate(s) for s in subsections]

    async def count_subsections(self, section_id: int) -> int:
        if not await self.section_repo.get_by_id(section_id):
            raise domain_errors.NotFoundError("Section not found")
        return await self.subsection_repo.count_by_section(section_id)

    async def list_materials(
        self,
        subsection_id: int,
        *,
        user: user_models.User,
        skip: int = core_pagination.DEFAULT_SKIP,
        limit: int = core_pagination.DEFAULT_LIMIT,
    ) -> list[theory_schemas.TheoryMaterialResponse]:
        if not await self.subsection_repo.get_by_id(subsection_id):
            raise domain_errors.NotFoundError("Subsection not found")

        if user.role == "teacher":
            materials = await self.material_repo.get_by_subsection(subsection_id, skip=skip, limit=limit)
        else:
            materials = await self.material_repo.get_published(subsection_id, skip=skip, limit=limit)

        return [theory_schemas.TheoryMaterialResponse.model_validate(m) for m in materials]

    async def count_materials(self, subsection_id: int, *, user: user_models.User) -> int:
        if not await self.subsection_repo.get_by_id(subsection_id):
            raise domain_errors.NotFoundError("Subsection not found")
        if user.role == "teacher":
            return await self.material_repo.count_by_subsection(subsection_id)
        return await self.material_repo.count_published_by_subsection(subsection_id)

    async def get_material(
        self,
        material_id: int,
        *,
        user: user_models.User,
    ) -> theory_schemas.TheoryMaterialResponse:
        material = await self.material_repo.get_by_id(material_id)
        if not material:
            raise domain_errors.NotFoundError("Theory material not found")

        if user.role != "teacher" and not material.is_published:
            raise domain_errors.ForbiddenError("Theory material is not published")

        return theory_schemas.TheoryMaterialResponse.model_validate(material)

