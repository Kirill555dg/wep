"""
Progress / aggregation response schemas.

These endpoints return derived metrics and should be strongly typed for OpenAPI client generation.
"""

import pydantic


class StudentProgressResponse(pydantic.BaseModel):
    total_homeworks: int
    completed: int
    in_progress: int
    not_started: int
    average_score_percentage: float
    total_attempts: int
    total_time_spent_minutes: int


class ClassroomProgressResponse(pydantic.BaseModel):
    total_students: int
    total_homeworks_assigned: int
    completed_homeworks: int
    average_completion_rate: float

