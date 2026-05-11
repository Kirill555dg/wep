"""
Problem management endpoints.
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
from app.api import http_errors
from app.api import pagination as api_pagination
from app.models import users as user_models
from app.schemas import pagination as pagination_schemas
from app.schemas import homework as homework_schemas
from app.services import problem as problem_service_module

router = fastapi.APIRouter()


@router.post(
    "",
    response_model=homework_schemas.ProblemFullResponse,
    status_code=http_status.HTTP_201_CREATED,
)
async def create_problem(
    problem_data: homework_schemas.ProblemCreate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """Create a new problem (teachers only)."""
    problem = await problem_service.create_problem(problem_data, current_user.id)
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.get("", response_model=pagination_schemas.Page[homework_schemas.ProblemFullResponse])
async def get_problems(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """Return all problems with full details (teachers only)."""
    problems = await problem_service.get_all_problems(pagination.skip, pagination.limit)
    total = await problem_service.count_all_problems()
    return pagination_schemas.Page(
        items=[homework_schemas.ProblemFullResponse.model_validate(p) for p in problems],
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{problem_id}", response_model=homework_schemas.ProblemFullResponse)
async def get_problem(
    problem_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """Return a problem by id (teachers only)."""
    problem = await problem_service.get_problem_by_id(problem_id)
    if problem is None:
        raise http_errors.not_found("Problem not found")
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.patch("/{problem_id}", response_model=homework_schemas.ProblemFullResponse)
async def update_problem(
    problem_id: int,
    problem_data: homework_schemas.ProblemUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """Update a problem (teachers only)."""
    problem = await problem_service.update_problem(problem_id, problem_data, current_user.id)
    if problem is None:
        raise http_errors.not_found("Problem not found")
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.delete("/{problem_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """Delete a problem (teachers only)."""
    deleted = await problem_service.delete_problem(problem_id, current_user.id)
    if not deleted:
        raise http_errors.not_found("Problem not found")
    return None
