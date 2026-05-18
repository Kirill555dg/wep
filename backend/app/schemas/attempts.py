import datetime as dt

import pydantic

from app.schemas import test_constructor as tc_schemas


class AttemptSummary(pydantic.BaseModel):
    id: int
    test_id: int
    test_title: str
    status: str
    score: int | None
    max_score: int | None
    started_at: dt.datetime
    finished_at: dt.datetime | None
    time_spent_minutes: int | None

    model_config = pydantic.ConfigDict(from_attributes=True)


class AttemptListResponse(pydantic.BaseModel):
    items: list[AttemptSummary]
    total: int


class ActiveAttemptResponse(pydantic.BaseModel):
    has_active: bool
    attempt_id: int | None
    status: str | None
    attempts_used: int


class BulkAnswersRequest(pydantic.BaseModel):
    answers: list[tc_schemas.AnswerSubmitRequest]


class BulkAnswersResponse(pydantic.BaseModel):
    saved: int
    errors: list[str] | None = None
