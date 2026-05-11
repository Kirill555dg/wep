"""
Tests for ProblemService
"""

import pytest

from app.domain import errors as domain_errors
from app.repositories import homework as homework_repository
from app.schemas import homework as homework_schemas
from app.services import problem as problem_service_module


pytestmark = pytest.mark.anyio


async def test_create_problem(db_session):
    """Test creating a new problem"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    problem_data = homework_schemas.ProblemCreate(
        title="Test Problem",
        description="This is a test problem",
        problem_type="multiple_choice",
        difficulty=3,
        correct_answer="A",
        explanation="Answer is A because...",
        hints="Think about option A",
    )

    problem = await problem_service.create_problem(problem_data, teacher_id=1)

    assert problem.title == "Test Problem"
    assert problem.description == "This is a test problem"
    assert problem.problem_type == "multiple_choice"
    assert problem.difficulty == 3


async def test_get_all_problems(db_session):
    """Test getting all problems"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    # Create multiple problems
    for i in range(3):
        problem_data = homework_schemas.ProblemCreate(
            title=f"Problem {i + 1}",
            description=f"Description {i + 1}",
            problem_type="text",
            correct_answer=f"Answer {i + 1}",
        )
        await problem_service.create_problem(problem_data, teacher_id=1)

    problems = await problem_service.get_all_problems()

    assert len(problems) == 3


async def test_get_problem_by_id(db_session):
    """Test getting a problem by ID"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    # Create a problem
    problem_data = homework_schemas.ProblemCreate(
        title="Find Me",
        description="Test problem for retrieval",
        problem_type="text",
        correct_answer="42",
    )
    created_problem = await problem_service.create_problem(problem_data, teacher_id=1)

    # Retrieve the problem
    problem = await problem_service.get_problem_by_id(created_problem.id)

    assert problem.title == "Find Me"
    assert problem.description == "Test problem for retrieval"


async def test_get_nonexistent_problem(db_session):
    """Test getting a problem that doesn't exist"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    with pytest.raises(domain_errors.NotFoundError):
        await problem_service.get_problem_by_id(99999)


async def test_update_problem(db_session):
    """Test updating a problem"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    # Create a problem
    problem_data = homework_schemas.ProblemCreate(
        title="Original Title",
        description="Original description",
        problem_type="text",
        correct_answer="Old answer",
    )
    created_problem = await problem_service.create_problem(problem_data, teacher_id=1)

    # Update the problem
    update_data = homework_schemas.ProblemUpdate(title="Updated Title", description="Updated description")
    updated_problem = await problem_service.update_problem(created_problem.id, update_data, teacher_id=1)

    assert updated_problem.title == "Updated Title"
    assert updated_problem.description == "Updated description"
    # Correct answer should remain unchanged
    assert updated_problem.correct_answer == "Old answer"


async def test_delete_problem(db_session):
    """Test deleting a problem"""
    problem_repo = homework_repository.ProblemRepository(db_session)
    problem_service = problem_service_module.ProblemService(problem_repo)

    # Create a problem
    problem_data = homework_schemas.ProblemCreate(
        title="To Be Deleted",
        description="This problem will be deleted",
        problem_type="text",
        correct_answer="Delete me",
    )
    created_problem = await problem_service.create_problem(problem_data, teacher_id=1)

    # Delete the problem
    result = await problem_service.delete_problem(created_problem.id, teacher_id=1)

    assert result is True

    # Verify problem is deleted
    with pytest.raises(domain_errors.NotFoundError):
        await problem_service.get_problem_by_id(created_problem.id)
