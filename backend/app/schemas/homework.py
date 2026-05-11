"""
Homework Pydantic schemas (DTOs)
"""

import datetime as dt

import pydantic


class HomeworkBase(pydantic.BaseModel):
    """Base homework fields"""

    title: str = pydantic.Field(..., min_length=1, max_length=255)
    description: str | None = None
    max_score: float = pydantic.Field(default=100.0, gt=0)
    deadline: dt.datetime | None = None


class HomeworkCreate(HomeworkBase):
    """Schema for creating homework"""

    lesson_id: int
    problem_ids: list[int] = pydantic.Field(default_factory=list)
    problem_points: list[float] | None = None  # Points for each problem


class HomeworkUpdate(pydantic.BaseModel):
    """Schema for updating homework"""

    title: str | None = pydantic.Field(None, min_length=1, max_length=255)
    description: str | None = None
    max_score: float | None = pydantic.Field(None, gt=0)
    deadline: dt.datetime | None = None
    is_published: bool | None = None


class HomeworkResponse(HomeworkBase):
    """Schema for homework response"""

    id: int
    lesson_id: int
    is_published: bool
    created_at: dt.datetime
    updated_at: dt.datetime
    problems_count: int = 0

    model_config = pydantic.ConfigDict(from_attributes=True)


class HomeworkDetailResponse(HomeworkResponse):
    """Detailed homework response with problems"""

    pass  # Can include problems list


# Problem schemas
class ProblemBase(pydantic.BaseModel):
    """Base problem fields"""

    title: str = pydantic.Field(..., min_length=1, max_length=255)
    description: str = pydantic.Field(..., min_length=1)
    problem_type: str  # Free-form type (e.g., text, multiple_choice)
    difficulty: int | str = pydantic.Field(default=1)
    correct_answer: str | None = None
    explanation: str | None = None
    hints: str | None = None  # JSON string


class ProblemCreate(ProblemBase):
    """Schema for creating a problem"""

    pass


class ProblemUpdate(pydantic.BaseModel):
    """Schema for updating a problem"""

    title: str | None = pydantic.Field(None, min_length=1, max_length=255)
    description: str | None = pydantic.Field(None, min_length=1)
    problem_type: str | None = None
    difficulty: str | None = None
    correct_answer: str | None = None
    explanation: str | None = None
    hints: str | None = None
    is_published: bool | None = None


class ProblemResponse(ProblemBase):
    """Schema for problem response (without correct answer for students)"""

    id: int
    is_published: bool
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class ProblemFullResponse(ProblemResponse):
    """Full problem response with correct answer (for teachers)"""

    correct_answer: str | None
    explanation: str | None


# Statistics schemas
class StatisticsBase(pydantic.BaseModel):
    """Base statistics fields"""

    status: str = pydantic.Field(default="not_started")
    score: float = pydantic.Field(default=0.0, ge=0)
    max_score: float
    time_spent_minutes: int = pydantic.Field(default=0, ge=0)


class StatisticsCreate(pydantic.BaseModel):
    """Schema for creating statistics (internal)"""

    student_id: int
    homework_id: int
    max_score: float


class StatisticsUpdate(pydantic.BaseModel):
    """Schema for updating statistics"""

    status: str | None = None
    score: float | None = pydantic.Field(None, ge=0)
    time_spent_minutes: int | None = pydantic.Field(None, ge=0)
    feedback: str | None = None


class StatisticsResponse(StatisticsBase):
    """Schema for statistics response"""

    id: int
    student_id: int
    homework_id: int
    attempts_count: int
    submitted_at: dt.datetime | None
    graded_at: dt.datetime | None
    feedback: str | None
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


# Answer submission
class AnswerSubmit(pydantic.BaseModel):
    """Schema for submitting an answer"""

    homework_id: int
    problem_id: int
    answer: str
    time_spent_minutes: int = pydantic.Field(default=0, ge=0)
