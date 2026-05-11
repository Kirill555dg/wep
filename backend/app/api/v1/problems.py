"""
Problem management endpoints
"""

import fastapi
from fastapi import status as http_status

from app.api import dependencies as deps
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
    """
    Create new problem (teachers only)

    - **title**: Problem title
    - **description**: Problem description/text
    - **problem_type**: Type of problem
    - **difficulty**: Difficulty level
    - **correct_answer**: Correct answer
    - **explanation**: Explanation of solution
    - **hints**: Hints (optional)
    """
    problem = await problem_service.create_problem(problem_data, current_user.id)
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.get("", response_model=pagination_schemas.Page[homework_schemas.ProblemFullResponse])
async def get_problems(
    pagination: api_pagination.Pagination = fastapi.Depends(api_pagination.get_pagination),
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """
    Get all problems (teachers only)

    Teachers can see all problems with correct answers
    """
    problems = await problem_service.get_all_problems(pagination.skip, pagination.limit)
    total = await problem_service.count_all_problems()
    return pagination_schemas.Page(
        items=[homework_schemas.ProblemFullResponse.model_validate(problem_item) for problem_item in problems],
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
    """
    Get problem by ID (teachers only)
    """
    problem = await problem_service.get_problem_by_id(problem_id)
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.patch("/{problem_id}", response_model=homework_schemas.ProblemFullResponse)
async def update_problem(
    problem_id: int,
    problem_data: homework_schemas.ProblemUpdate,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """
    Update problem (teachers only)
    """
    problem = await problem_service.update_problem(problem_id, problem_data, current_user.id)
    return homework_schemas.ProblemFullResponse.model_validate(problem)


@router.delete("/{problem_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_problem(
    problem_id: int,
    current_user: user_models.User = fastapi.Depends(deps.get_current_teacher),
    problem_service: problem_service_module.ProblemService = fastapi.Depends(deps.get_problem_service),
):
    """
    Delete problem (teachers only)
    """
    await problem_service.delete_problem(problem_id, current_user.id)
    return None
