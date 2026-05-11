"""
Theory content endpoints (subjects/sections/subsections/materials).
"""

import fastapi

from app.api import dependencies as deps
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import theory as theory_schemas
from app.services import theory as theory_service_module


router = fastapi.APIRouter()


@router.get("/subjects", response_model=pagination_schemas.Page[theory_schemas.SubjectResponse])
async def list_subjects(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    items = await theory_service.list_subjects(skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_subjects()
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/subjects/{subject_id}", response_model=theory_schemas.SubjectResponse)
async def get_subject(
    subject_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    return await theory_service.get_subject(subject_id)


@router.get(
    "/subjects/{subject_id}/sections",
    response_model=pagination_schemas.Page[theory_schemas.SectionResponse],
)
async def list_sections(
    subject_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    items = await theory_service.list_sections(subject_id, skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_sections(subject_id)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/sections/{section_id}/subsections",
    response_model=pagination_schemas.Page[theory_schemas.SubsectionResponse],
)
async def list_subsections(
    section_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    items = await theory_service.list_subsections(section_id, skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_subsections(section_id)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get(
    "/subsections/{subsection_id}/materials",
    response_model=pagination_schemas.Page[theory_schemas.TheoryMaterialResponse],
)
async def list_materials(
    subsection_id: int,
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    items = await theory_service.list_materials(
        subsection_id,
        user=current_user,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    total = await theory_service.count_materials(subsection_id, user=current_user)
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/materials/{material_id}", response_model=theory_schemas.TheoryMaterialResponse)
async def get_material(
    material_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    return await theory_service.get_material(material_id, user=current_user)

