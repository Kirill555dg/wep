"""
Theory content endpoints (subjects / sections / subsections / materials).
"""

import fastapi

from app.api import dependencies as deps
from app.api import http_errors
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import theory as theory_schemas
from app.services import exceptions as service_exceptions
from app.services import theory as theory_service_module

router = fastapi.APIRouter()


@router.get("/subjects", response_model=pagination_schemas.Page[theory_schemas.SubjectResponse])
async def list_subjects(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    """Return all active subjects."""
    items = await theory_service.list_subjects(skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_subjects()
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/subjects/{subject_id}", response_model=theory_schemas.SubjectResponse)
async def get_subject(
    subject_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    """Return a subject by id."""
    result = await theory_service.get_subject(subject_id)
    if result is None:
        raise http_errors.not_found("Subject not found")
    return result


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
    """Return sections for a subject."""
    items = await theory_service.list_sections(subject_id, skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_sections(subject_id)
    if items is None or total is None:
        raise http_errors.not_found("Subject not found")
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
    """Return subsections for a section."""
    items = await theory_service.list_subsections(section_id, skip=pagination.skip, limit=pagination.limit)
    total = await theory_service.count_subsections(section_id)
    if items is None or total is None:
        raise http_errors.not_found("Section not found")
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
    """Return theory materials for a subsection."""
    items = await theory_service.list_materials(
        subsection_id, user=current_user, skip=pagination.skip, limit=pagination.limit,
    )
    total = await theory_service.count_materials(subsection_id, user=current_user)
    if items is None or total is None:
        raise http_errors.not_found("Subsection not found")
    return pagination_schemas.Page(items=items, total=total, skip=pagination.skip, limit=pagination.limit)


@router.get("/materials/{material_id}", response_model=theory_schemas.TheoryMaterialResponse)
async def get_material(
    material_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_user),
    theory_service: theory_service_module.TheoryService = fastapi.Depends(deps.get_theory_service),
):
    """Return a theory material; students cannot access unpublished materials."""
    try:
        result = await theory_service.get_material(material_id, user=current_user)
    except service_exceptions.ServiceError as exc:
        if exc.code == "unpublished":
            raise http_errors.forbidden(exc.message, code=exc.code)
        raise
    if result is None:
        raise http_errors.not_found("Theory material not found")
    return result
