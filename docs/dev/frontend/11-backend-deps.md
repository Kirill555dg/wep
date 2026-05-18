# Backend Dependencies

Новый функционал фронтенда требует изменений на бэкенде. Ниже — что нужно добавить/изменить.

## Новые question types

### MATCHING (сопоставление)

> **Deferred / pending backend.** Matching needs rethinking because options must be Typst-rendered. Will be revisited later.

### FILE_UPLOAD

- Добавить `FILE_UPLOAD` в `QuestionType` enum
- No auto-grading (manual review or "submitted" status)
- Разрешённые типы файлов: ограничить на уровне валидации
- Max file size: настраивается (например 10MB)
- Answer support: `Answer.file_url` stores the uploaded file reference (MinIO)

## Test <-> Question relationship

> **Not needed — marked as future feature request.** Question reuse (many-to-many via `TestQuestion` bridge) is out of scope for now. Keep current `Question.test_id` one-to-many.

## User profile update endpoint

Сейчас нет `PATCH /users/me`:

```python
PATCH /api/v1/users/me
Request: UserUpdate(first_name?, last_name?, middle_name?, username?, email?)
Response: UserResponse
```

## Avatar upload

- Upload to MinIO, set `avatar_url` on User
- `POST /api/v1/users/me/avatar` (multipart)
- Delete old avatar on update

## Statistics endpoints

### Calendar data

```python
GET /api/v1/stats/calendar?year=2026&month=4
Response: {
    "days": {
        "2026-04-01": 3,  # attempts count
        "2026-04-02": 0,
        ...
    }
}
```

### Test stats (obezlichennaya)

```python
GET /api/v1/stats/tests/{test_id}  # for test view page
Response: {
    "total_attempts": 120,
    "completed_attempts": 98,
    "avg_score": 82.5,
    "avg_score_percent": 82.5,
    "avg_time_minutes": 15.2,
    "score_distribution": {
        "0-20": 5,
        "21-40": 12,
        "41-60": 25,
        "61-80": 35,
        "81-100": 23
    },
    "question_stats": [
        {"question_id": 1, "correct_count": 90, "total_count": 98},
        ...
    ],
    "daily_scores": [
        {"date": "2026-03-01", "avg_score": 80, "count": 5},
        ...
    ]
}
```

### Attempt stats per user

```python
GET /api/v1/stats/users/{user_id}/attempts  # author can see others' stats
GET /api/v1/stats/me/attempts  # own history (for history page)
Response: Page[AttemptSummary]
```

## Media for test (cover + completion)

Сейчас медиа только у вопросов. Нужно расширить:

```python
# Media model (generalized)
class Media(Base):
    __tablename__ = "media"
    id: int
    owner_type: str  # "question", "test", "completion"
    owner_id: int    # question.id, test.id
    file_url: str
    file_type: str   # image/audio/video
    order_number: int
    created_at: datetime

# Или добавить JSON-поля в Test:
# test.cover_image_url
# test.completion_message (text)
# test.completion_media (list of file IDs)
```

## Ссылки для шаринга

```python
# Share links for tests
class ShareLink(Base):
    __tablename__ = "share_links"
    id: int
    test_id: int (FK)
    code: str  # unique short code
    max_uses: int | None  # None = unlimited, 1 = one-time
    current_uses: int
    expires_at: datetime | None
    created_by: int (FK → users.id)
    is_active: bool

# Endpoints:
POST /api/v1/tests/{test_id}/share
  Request: { "max_uses": 1, "expires_in_hours": 48 }
  Response: { "code": "abc123", "url": "/share/abc123" }

GET /share/{code}
  → resolves to test, increments uses if limited
  Redirect: /tests/{test_id}

# One-time links: after use, link is invalidated
```

## Catalog — filter by author

```python
GET /api/v1/catalog/?author_id=X  # already has q, tags, skip, limit
```

## Tags — search

```python
GET /api/v1/tags/?q=math
Response: list[TagResponse]  # filtered by name containing "math", sorted by usage
```

## Completion screen data

В `AttemptResultResponse` добавить:

```python
class AttemptResultResponse:
    ...
    completion_message: str | None  # Typst text from test settings
    completion_media: list[MediaResponse]  # from test settings
```

## Attempt limits

```python
class TestCreate(BaseModel):
    ...
    attempt_limit: Optional[int]  # default None for public, 1 for private (None = unlimited)
```

```python
class Test(BaseModel):
    ...
    attempt_limit: Optional[int]
    # None = unlimited attempts
    # Note: attempt_limit is not exposed to public API consumers; only visible in author detail view
```

## Test settings

```python
PATCH /api/v1/tests/{id}/settings
Request: {
    "title": str?,
    "description": str?,
    "tags": list[int]?,         # tag IDs
    "visibility": str?,         # "public" | "private"
    "attempt_limit": int?,
    "time_limit_minutes": int?,
    "completion_message": str?,
    "completion_media": list[int]?  # media IDs
}
Response: TestResponse
```

## Track time toggle

```python
PATCH /api/v1/tests/{id}/track-time
Request: { "track_time": bool }
Response: TestResponse
```

## Resume attempt

```python
PATCH /api/v1/attempts/{id}
Request: {
    "cached_answers": list[AnswerPayload]  # previously saved answers
}
Response: AttemptResponse
```

## Bulk answer submission

```python
POST /api/v1/attempts/{id}/bulk_answers
Request: {
    "answers": list[AnswerPayload]
}
Response: AttemptResultResponse
```

## Summary of new/needed endpoints

| Method | Path | Purpose |
|---|---|---|
| PATCH | `/api/v1/users/me` | Update profile |
| PATCH | `/api/v1/tests/{id}/settings` | Update test meta |
| PATCH | `/api/v1/tests/{id}/track-time` | Toggle track time |
| PATCH | `/api/v1/attempts/{id}` | Resume attempt (cached answers) |
| POST | `/api/v1/attempts/{id}/bulk_answers` | Submit all answers at once |
| GET | `/api/v1/stats/calendar` | Activity calendar |
| GET | `/api/v1/stats/tests/{id}` | Extended test stats |
| GET | `/api/v1/stats/users/{id}/attempts` | User attempts (author view) |
| GET | `/api/v1/tags/?q=` | Tag search |
| POST | `/api/v1/tests/{id}/share` | Create share link |
| GET | `/share/{code}` | Resolve share link |
| PATCH | `/api/v1/tests/{id}/questions/{qid}/reorder` | Reorder questions |

## Schema changes needed

| Change | File |
|---|---|
| Add `FILE_UPLOAD` to `QuestionType` | `models/test_constructor.py` |
| Add `Media` model | `models/test_constructor.py` |
| Add `ShareLink` model | `models/test_constructor.py` |
| Add `completion_message`, `completion_media_ids` to Test | `models/test_constructor.py` |
| Add `attempt_limit` to `Test` model and `TestCreate` schema | `models/test_constructor.py`, `schemas/test_constructor.py` |
| Add `file_url` to Answer (for FILE_UPLOAD answers) | `models/test_constructor.py` |
| Add `avatar_url` to User (already exists) | — |
| Add `test_id` to Answer (optional, for easier querying) | `models/test_constructor.py` |
| *(Deferred)* `MATCHING` / `MatchPair` | pending Typst-rendered options redesign |
| *(Future feature)* `TestQuestion` bridge (M2M) for question reuse | future request |
