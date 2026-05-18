import datetime as dt
import enum as pydantic_enum

import pydantic


# --- Question Types (Pydantic Enums for API validation) ---

class QuestionType(str, pydantic_enum.Enum):
    SINGLE_CHOICE = "SINGLE_CHOICE"
    MULTIPLE_CHOICE = "MULTIPLE_CHOICE"
    TEXT = "TEXT"
    ESSAY = "ESSAY"
    MATCHING = "MATCHING"
    FILE_UPLOAD = "FILE_UPLOAD"


class AttemptStatus(str, pydantic_enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


# --- Tag ---

class TagCreate(pydantic.BaseModel):
    name: str = pydantic.Field(..., min_length=1, max_length=100)


class TagResponse(pydantic.BaseModel):
    id: int
    name: str
    slug: str

    model_config = pydantic.ConfigDict(from_attributes=True)


# --- Option ---

class OptionCreate(pydantic.BaseModel):
    text: str = pydantic.Field(..., min_length=1)
    is_correct: bool = False
    order_number: int = pydantic.Field(default=0, ge=0)


class OptionUpdate(pydantic.BaseModel):
    text: str | None = pydantic.Field(None, min_length=1)
    is_correct: bool | None = None
    order_number: int | None = pydantic.Field(None, ge=0)


class OptionResponse(pydantic.BaseModel):
    id: int
    text: str
    order_number: int

    model_config = pydantic.ConfigDict(from_attributes=True)


class OptionAuthorResponse(OptionResponse):
    is_correct: bool


# --- Question ---

class QuestionCreate(pydantic.BaseModel):
    question_type: QuestionType
    text: str = pydantic.Field(..., min_length=1)
    order_number: int = pydantic.Field(default=0, ge=0)
    points: int = pydantic.Field(default=1, ge=1)
    explanation: str | None = None
    correct_answer: str | None = None
    image_url: str | None = None
    media_files: list[str] = pydantic.Field(default_factory=list)
    options: list[OptionCreate] = pydantic.Field(default_factory=list)
    question_data: dict[str, object] | None = None


class QuestionUpdate(pydantic.BaseModel):
    question_type: QuestionType | None = None
    text: str | None = pydantic.Field(None, min_length=1)
    order_number: int | None = pydantic.Field(None, ge=0)
    points: int | None = pydantic.Field(None, ge=1)
    explanation: str | None = None
    correct_answer: str | None = None
    image_url: str | None = None
    media_files: list[str] = pydantic.Field(default_factory=list)
    options: list[OptionCreate] | None = None
    question_data: dict[str, object] | None = None


class QuestionResponse(pydantic.BaseModel):
    id: int
    question_type: QuestionType
    text: str
    order_number: int
    points: int
    image_url: str | None
    media_files: list[str] = []
    options: list[OptionResponse] = []
    question_data: dict[str, object] | None = None

    model_config = pydantic.ConfigDict(from_attributes=True)


class QuestionAuthorResponse(pydantic.BaseModel):
    id: int
    question_type: QuestionType
    text: str
    order_number: int
    points: int
    explanation: str | None
    correct_answer: str | None
    image_url: str | None
    media_files: list[str] = []
    options: list[OptionAuthorResponse] = []
    question_data: dict[str, object] | None = None

    model_config = pydantic.ConfigDict(from_attributes=True)


class QuestionPoolResponse(pydantic.BaseModel):
    id: int
    question_type: QuestionType
    text: str
    points: int
    created_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


# --- Test ---

class TestCreate(pydantic.BaseModel):
    title: str = pydantic.Field(..., min_length=1, max_length=255)
    description: str | None = None
    is_public: bool = False
    time_limit_minutes: int | None = pydantic.Field(None, ge=1)
    attempt_limit: int | None = pydantic.Field(None, ge=1)
    track_time: bool = True
    completion_message: str | None = None
    image_url: str | None = None
    media_files: list[str] = pydantic.Field(default_factory=list)
    tag_names: list[str] = pydantic.Field(default_factory=list)


class TestUpdate(pydantic.BaseModel):
    title: str | None = pydantic.Field(None, min_length=1, max_length=255)
    description: str | None = None
    is_public: bool | None = None
    time_limit_minutes: int | None = pydantic.Field(None, ge=1)
    attempt_limit: int | None = pydantic.Field(None, ge=1)
    track_time: bool | None = None
    completion_message: str | None = None
    image_url: str | None = None
    media_files: list[str] = pydantic.Field(default_factory=list)
    tag_names: list[str] | None = None


class TestResponse(pydantic.BaseModel):
    id: int
    author_id: int
    author_name: str = ""
    author_login: str = ""
    title: str
    description: str | None
    is_public: bool
    time_limit_minutes: int | None
    track_time: bool
    image_url: str | None = None
    media_files: list[str] = []
    questions_count: int = 0
    tags: list[TagResponse] = []
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = pydantic.ConfigDict(from_attributes=True)


class TestDetailResponse(TestResponse):
    questions: list[QuestionResponse] = []


class TestAuthorDetailResponse(TestResponse):
    attempt_limit: int | None
    completion_message: str | None
    questions: list[QuestionAuthorResponse] = []


# --- Attempt List (for History) ---

class AttemptListItem(pydantic.BaseModel):
    id: int
    test_id: int
    test_title: str
    status: AttemptStatus
    score: int | None
    max_score: int | None
    started_at: dt.datetime
    finished_at: dt.datetime | None
    time_spent_minutes: int | None  # computed or stored

    model_config = pydantic.ConfigDict(from_attributes=True)


# --- Calendar ---

class CalendarDayData(pydantic.BaseModel):
    date: str  # "2026-05-18"
    count: int
    tests: list[str]  # test titles taken that day


class CalendarMonthResponse(pydantic.BaseModel):
    year: int
    month: int
    days: dict[str, int]  # {"2026-05-01": 3, "2026-05-02": 0, ...}


# --- Catalog ---

class CatalogSearchParams(pydantic.BaseModel):
    q: str | None = None
    tags: list[str] = pydantic.Field(default_factory=list)
    author_id: int | None = None
    author_login: str | None = None
    skip: int = pydantic.Field(default=0, ge=0)
    limit: int = pydantic.Field(default=20, ge=1, le=100)


# --- Attempt ---

class AttemptStartRequest(pydantic.BaseModel):
    test_id: int


class AttemptResponse(pydantic.BaseModel):
    id: int
    test_id: int
    user_id: int
    status: AttemptStatus
    started_at: dt.datetime
    finished_at: dt.datetime | None
    expires_at: dt.datetime | None
    score: int | None
    max_score: int | None

    model_config = pydantic.ConfigDict(from_attributes=True)


class AnswerSubmitRequest(pydantic.BaseModel):
    question_id: int
    selected_option_ids: list[int] | None = None
    text_answer: str | None = None
    matching_answer: dict[str, int] | None = None
    file_answer: str | None = None


class AnswerResponse(pydantic.BaseModel):
    id: int
    question_id: int
    selected_option_ids: list[int] | None
    text_answer: str | None
    matching_answer: dict[str, int] | None = None
    file_answer: str | None = None
    is_correct: bool | None
    points_earned: int | None

    model_config = pydantic.ConfigDict(from_attributes=True)


class AttemptAnswerDetail(pydantic.BaseModel):
    question_id: int
    question_text: str
    question_type: QuestionType
    points: int
    selected_option_ids: list[int] | None
    text_answer: str | None
    matching_answer: dict[str, int] | None = None
    file_answer: str | None = None
    is_correct: bool | None
    points_earned: int | None
    correct_option_ids: list[int]
    explanation: str | None


class AttemptResultResponse(pydantic.BaseModel):
    attempt_id: int
    test_id: int
    test_title: str
    status: AttemptStatus
    score: int
    max_score: int
    started_at: dt.datetime
    finished_at: dt.datetime | None
    expires_at: dt.datetime | None
    answers: list[AttemptAnswerDetail] = []


# --- Stats ---

class TestStatsResponse(pydantic.BaseModel):
    test_id: int
    test_title: str
    total_attempts: int
    completed_attempts: int
    avg_score: float | None
    avg_score_percent: float | None


class AuthorStatsResponse(pydantic.BaseModel):
    total_tests: int
    public_tests: int
    total_attempts_received: int
    completed_attempts_received: int


class ScoreDistributionResponse(pydantic.BaseModel):
    bucket_0_20: int = 0
    bucket_20_40: int = 0
    bucket_40_60: int = 0
    bucket_60_80: int = 0
    bucket_80_100: int = 0


class PerQuestionStat(pydantic.BaseModel):
    question_id: int
    question_text: str
    total_attempts: int
    correct_attempts: int
    correct_percent: float


class PerQuestionStatsResponse(pydantic.BaseModel):
    items: list[PerQuestionStat]
