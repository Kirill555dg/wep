# Backend TODO — что нужно доделать на сервере

Этот документ содержит полный список endpoint'ов и изменений, которые необходимо добавить в backend для соответствия frontend-дизайну.

Каждый пункт — самодостаточная задача. Передаётся сабагенту как инструкция.

---

## Краткий обзор текущего состояния бэкенда

**Есть (28 endpoint'ов):**
- Auth: register, login, me
- Tests: CRUD + questions CRUD (POST/PATCH/DELETE)
- Catalog: search (by q + tags), get public test
- Tags: list, create
- Attempts: start, get, submit single answer, finish, get result
- Stats: author stats, per-test stats
- Media: upload to MinIO
- Root + health + ping

**Нет (7 gap'ов):**

| # | Gap | Критичность | Где нужно |
|---|---|---|---|
| 1 | List user attempts | 🔴 Высокая | History page |
| 2 | Active attempt lookup | 🔴 Высокая | Test View page — "Continue" CTA |
| 3 | Calendar stats | 🟡 Средняя | History page — activity calendar |
| 4 | Bulk answer submit | 🟡 Средняя | Test taking — финализация попытки |
| 5 | Patch user profile | 🟡 Средняя | Profile page |
| 6 | Catalog filter by author_id | 🟢 Низкая | Catalog — "тесты автора" |
| 7 | Share links | 🟢 Низкая | One-time private links |

---

## 1. GET /api/v1/attempts (список попыток текущего пользователя)

### Цель

History page (`/history`) отображает список всех прохождений тестов текущим пользователем: test title, score, max_score, date, time_spent.

### Endpoint

```
GET /api/v1/attempts
```

### Query parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `skip` | int | 0 | Offset |
| `limit` | int | 20 | Page size (max 100) |
| `status` | str | — | Filter by status: `in_progress`, `completed`, `expired`, `abandoned` |
| `test_id` | int | — | Filter by specific test |
| `date_from` | ISO date | — | Filter attempts after date |
| `date_to` | ISO date | — | Filter attempts before date |

### Response

```python
# schemas/attempts.py (NEW FILE or extend test_constructor.py)

class AttemptSummary(pydantic.BaseModel):
    id: int
    test_id: int
    test_title: str
    status: str
    score: int | None
    max_score: int | None
    started_at: dt.datetime
    finished_at: dt.datetime | None
    time_spent_minutes: int | None  # or seconds, see details below

class AttemptListResponse(pydantic.BaseModel):
    items: list[AttemptSummary]
    total: int
```

### Логика

```python
# app/api/v1/attempts.py

@router.get("/", response_model=Page[AttemptSummary])
async def list_my_attempts(
    skip: int = 0,
    limit: int = 20,
    status: str | None = None,
    test_id: int | None = None,
    date_from: dt.datetime | None = None,
    date_to: dt.datetime | None = None,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    query = (
        select(Attempt.id, Attempt.test_id, Test.title.label("test_title"),
               Attempt.status, Attempt.score, Attempt.max_score,
               Attempt.started_at, Attempt.finished_at)
        .join(Test, Attempt.test_id == Test.id)
        .where(Attempt.user_id == current_user.id)
        .order_by(Attempt.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    
    if status:
        query = query.where(Attempt.status == status)
    if test_id:
        query = query.where(Attempt.test_id == test_id)
    if date_from:
        query = query.where(Attempt.created_at >= date_from)
    if date_to:
        query = query.where(Attempt.created_at <= date_to)
    
    result = await db.execute(query)
    rows = result.mappings().all()
    
    # Compute time_spent for each
    items = []
    for row in rows:
        minutes = None
        if row.finished_at and row.started_at:
            minutes = int((row.finished_at - row.started_at).total_seconds() / 60)
        items.append(AttemptSummary(
            id=row.id,
            test_id=row.test_id,
            test_title=row.test_title,
            status=row.status,
            score=row.score,
            max_score=row.max_score,
            started_at=row.started_at,
            finished_at=row.finished_at,
            time_spent_minutes=minutes,
        ))
    
    total = await db.scalar(select(func.count(Attempt.id)).where(Attempt.user_id == current_user.id))
    return Page(items=items, total=total, skip=skip, limit=limit)
```

### Репозиторий

Добавить в `app/repositories/test_constructor.py`:

```python
class AttemptRepository extends BaseRepository:
    async def list_by_user(
        self, user_id: int, skip: int = 0, limit: int = 20,
        status: str | None = None, test_id: int | None = None,
    ) -> tuple[list[Attempt], int]:
        ...
```

### Критичность

🔴 **Высокая** — без этого History page не покажет список прохождений.

---

## 2. GET /api/v1/attempts/active (проверка активной попытки)

### Цель

Когда пользователь открывает страницу теста (`/tests/:id`), нужно знать: есть ли у него незавершённая попытка этого теста?

Это определяет CTA:
- `[Начать тест]` — попытки нет
- `[Продолжить тест]` — есть `in_progress` попытка
- `[Пройти снова]` — была завершена, лимит позволяет

### Endpoint

```
GET /api/v1/attempts/active?test_id=X
```

### Query parameters

| Param | Type | Description |
|---|---|---|
| `test_id` | int | ID теста (required) |

### Response

```python
class ActiveAttemptResponse(pydantic.BaseModel):
    has_active: bool
    attempt_id: int | None
    status: str | None  # "in_progress" | "completed" | etc.
    attempts_used: int  # сколько всего попыток было у пользователя на этот тест
```

### Логика

```python
@router.get("/active", response_model=ActiveAttemptResponse)
async def get_active_attempt(
    test_id: int,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    # Count all attempts for this user + test
    stmt_total = select(func.count(Attempt.id)).where(
        Attempt.user_id == current_user.id,
        Attempt.test_id == test_id,
    )
    total = await db.scalar(stmt_total)
    
    # Find active (in_progress) attempt
    stmt_active = select(Attempt).where(
        Attempt.user_id == current_user.id,
        Attempt.test_id == test_id,
        Attempt.status == "in_progress",
    ).order_by(Attempt.created_at.desc())
    
    result = await db.execute(stmt_active)
    active = result.scalar()
    
    return ActiveAttemptResponse(
        has_active=active is not None,
        attempt_id=active.id if active else None,
        status=active.status if active else None,
        attempts_used=total,
    )
```

### Альтернатива

Можно не делать отдельный endpoint, а расширить `GET /tests/{id}` для авторизованных пользователей:
-漂亮 подход: в `TestDetailResponse` или `TestAuthorDetailResponse` добавить поле `user_attempt_summary: ActiveAttemptResponse | None`.
- Но это загрязняет схему. Лучше отдельный endpoint.

### Критичность

🔴 **Высокая** — без этого CTA на Test View не работает.

---

## 3. GET /api/v1/stats/calendar (календарь активности)

### Цель

History page рисует GitHub-style heatmap: сколько тестов пройдено по каждому дню месяца.

### Endpoint

```
GET /api/v1/stats/calendar?year=2026&month=5
```

### Query parameters

| Param | Type | Default | Description |
|---|---|---|---|
| `year` | int | current | Год |
| `month` | int | current | Месяц (1-12) |

### Response

```python
class CalendarDay(pydantic.BaseModel):
    date: str  # "2026-05-01"
    count: int  # количество завершённых попыток в этот день
    total_score: int | None  # суммарный балл (опционально)

class CalendarResponse(pydantic.BaseModel):
    year: int
    month: int
    days: dict[str, int]  # { "2026-05-01": 3, "2026-05-02": 0, ... }
```

### Логика

```python
@router.get("/calendar", response_model=CalendarResponse)
async def get_calendar(
    year: int = Query(default_factory=lambda: dt.datetime.now().year),
    month: int = Query(default_factory=lambda: dt.datetime.now().month),
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    start_date = dt.datetime(year, month, 1, tzinfo=dt.timezone.utc)
    if month == 12:
        end_date = dt.datetime(year + 1, 1, 1, tzinfo=dt.timezone.utc)
    else:
        end_date = dt.datetime(year, month + 1, 1, tzinfo=dt.timezone.utc)
    
    stmt = (
        select(
            func.date_trunc('day', Attempt.created_at).label("day"),
            func.count(Attempt.id).label("count"),
        )
        .where(
            Attempt.user_id == current_user.id,
            Attempt.status == "completed",
            Attempt.created_at >= start_date,
            Attempt.created_at < end_date,
        )
        .group_by(func.date_trunc('day', Attempt.created_at))
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # Build map of all days in month
    days_in_month = calendar.monthrange(year, month)[1]
    days = {}
    for d in range(1, days_in_month + 1):
        date_str = f"{year}-{month:02d}-{d:02d}"
        days[date_str] = 0
    
    for row in rows:
        date_str = row.day.strftime("%Y-%m-%d")
        days[date_str] = row.count
    
    return CalendarResponse(year=year, month=month, days=days)
```

### Критичность

🟡 **Средняя** — History page работает и без календаря (показывает только список), но calendar — ключевая визуальная фича.

---

## 4. POST /api/v1/attempts/{id}/bulk-answers (массовая отправка ответов)

### Цель

При нажатии `[Submit All]` во время прохождения теста пользователь отправляет ВСЕ накопленные ответы за один запрос, а затем finish.

Текущий `finish` (`POST /attempts/{id}/finish`) не принимает body — он просто ставит статус `completed` и считает score по уже сохранённым в БД ответам.

Проблема: при take mode ответы кэшируются в localStorage. Если пользователь не нажимал `[Submit]` для каждого отдельного ответа, а нажал только `[Submit All]` в конце, то answers в БД не сохранены.

### Вариант A: bulk-answers endpoint (лучше)

```
POST /api/v1/attempts/{attempt_id}/bulk-answers
```

### Request body

```python
class BulkAnswersRequest(pydantic.BaseModel):
    answers: list[AnswerSubmitRequest]  # массив { question_id, selected_option_ids, text_answer }
```

### Response

```python
class BulkAnswersResponse(pydantic.BaseModel):
    saved: int  # сколько сохранено
    errors: list[str] | None  # если partial failure
```

### Логика

```python
@router.post("/{attempt_id}/bulk-answers", response_model=BulkAnswersResponse)
async def submit_bulk_answers(
    attempt_id: int,
    data: BulkAnswersRequest,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    attempt = await attempt_repo.get_by_id(attempt_id)
    if not attempt or attempt.user_id != current_user.id:
        raise forbidden()
    
    saved = 0
    for ans in data.answers:
        # Check answer belongs to this attempt's test
        question = await question_repo.get_by_id(ans.question_id)
        if question and question.test_id == attempt.test_id:
            await answer_repo.create_or_update(
                attempt_id=attempt_id,
                question_id=ans.question_id,
                selected_option_ids=ans.selected_option_ids,
                text_answer=ans.text_answer,
            )
            saved += 1
    
    return BulkAnswersResponse(saved=saved)
```

### Вариант B: make finish accept body (проще, менее гибко)

Сделать `POST /attempts/{id}/finish` body-optional:
- Если body = null — finish без body (current behavior)
- Если body = `{ answers: [...] }` — сначала сохранить bulk answers, потом finish

```python
class FinishAttemptRequest(pydantic.BaseModel):
    answers: list[AnswerSubmitRequest] | None = None
```

### Критичность

🟡 **Средняя** — можно обойти, если frontend делает `submitAnswer` для каждого вопроса при каждом изменении. Но это создаёт много запросов. Bulk лучше.

---

## 5. PATCH /api/v1/users/me (обновление профиля)

### Цель

Profile page (`/profile`) позволяет редактировать: first_name, last_name, middle_name, username, email.

### Endpoint

```
PATCH /api/v1/users/me
```

### Request body

```python
class UserUpdate(pydantic.BaseModel):
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    middle_name: str | None = Field(None, max_length=100)
    username: str | None = Field(None, min_length=3, max_length=100)
    email: str | None = Field(None, max_length=100)  # лучше EmailStr, но проверить pydantic
```

### Response

```python
class UserResponse(...):  # already exists in schemas/users.py
```

### Логика

```python
# app/api/v1/users.py (NEW FILE)

from app.models import users as user_models
from app.schemas import users as user_schemas

router = APIRouter()

@router.patch("/me", response_model=user_schemas.UserResponse)
async def update_me(
    data: user_schemas.UserUpdate,
    current_user = Depends(get_current_user),
    db = Depends(get_db),
):
    # Update user
    update_data = data.model_dump(exclude_none=True)
    if update_data:
        user_repo = UserRepository(db)
        await user_repo.update(current_user.id, update_data)
    
    return current_user  # или refetch
```

### Репозиторий

`UserRepository` уже есть в `app/repositories/user.py`. Если `update` не реализован — добавить:

```python
class UserRepository(BaseRepository):
    async def update(self, user_id: int, data: dict):
        stmt = update(User).where(User.id == user_id).values(**data)
        await self.db.execute(stmt)
        await self.db.commit()
```

### Avatar upload

Avatar — через уже существующий `POST /api/v1/media/upload`:
1. Frontend загружает аватар → получает URL
2. Frontend PATCH `/users/me` с `avatar_url: <url>`

### Критичность

🟡 **Средняя** — profile page можно показать readonly, но обновление — core feature.

---

## 6. Catalog filter by author_id

### Цель

В Catalog (ISLAND-1) и на странице автора (ISLAND-3) можно кликнуть на имя автора и отфильтровать каталог по этому автору.

### Что нужно

Добавить `author_id` в `CatalogSearchParams` и реализовать фильтрацию в `CatalogService`.

### Изменения

```python
# app/schemas/test_constructor.py

class CatalogSearchParams(pydantic.BaseModel):
    q: str | None = None
    tags: list[str] = Field(default_factory=list)
    author_id: int | None = None  # ← NEW
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
```

```python
# app/services/catalog_service.py

async def search(self, params: CatalogSearchParams) -> tuple[list[Test], int]:
    query = select(Test).where(Test.is_public == True)
    
    if params.q:
        query = query.where(
            or_(Test.title.ilike(f"%{params.q}%"), Test.description.ilike(f"%{params.q}%"))
        )
    if params.tags:
        tag_ids = [t.id for t in await self.tag_repo.get_by_names(params.tags)]
        query = query.join(TestTag).where(TestTag.tag_id.in_(tag_ids))
    if params.author_id:  # ← NEW
        query = query.where(Test.author_id == params.author_id)
    
    total = await self.db.scalar(select(func.count()).select_from(query))
    query = query.offset(params.skip).limit(params.limit)
    
    result = await self.db.execute(query)
    tests = result.scalars().all()
    return tests, total
```

### Критичность

🟢 **Низкая** — можно отложить, catalog работает без этого.

---

## 7. Share links (одноразовые ссылки на приватные тесты)

### Цель

Приватный тест можно поделить короткой ссылкой. Лимит на использование — одноразовый или многоразовый.

### Часть из дизайна:

- Тест view (ISLAND-3) — `[Share]` кнопка (если автор)
- Генерация: `POST /api/v1/tests/{id}/share` → `{ code, url }`
- Открытие: `GET /share/{code}` → test view с `?shared=abc123`

### Минимальная реализация (MVP)

На первом этапе это можно реализовать очень просто:

```python
# app/api/v1/tests.py

@router.post("/{test_id}/share")
async def create_share_link(
    test_id: int,
    data: ShareLinkCreate,  # { max_uses: int | None }
    current_user = Depends(get_current_user),
    ...
):
    # Generate short code (nanoid, 8 chars)
    code = generate_token(8)
    # Store in new table or redis
    # For MVP: store in DB table `share_links`
    ...
    return {"code": code, "url": f"/share/{code}"}
```

Но можно отложить: share links — низкий приоритет.

### Критичность

🟢 **Низкая** — feature request.

---

## Сводка для backend-разработчика

### Приоритеты

| Приоритет | Endpoint | Зачем |
|---|---|---|
| 🔴 **P0** | `GET /attempts` | History page — список прохождений |
| 🔴 **P0** | `GET /attempts/active` | Test View — CTA Start/Continue/Retake |
| 🟡 **P1** | `POST /attempts/{id}/finish` + body | Test taking — bulk submit |
| 🟡 **P1** | `PATCH /users/me` | Profile — редактирование |
| 🟡 **P1** | `GET /stats/calendar` | History — activity calendar |
| 🟢 **P2** | `author_id` in catalog | Catalog — фильтр по автору |
| 🟢 **P2** | Share links | One-time private sharing |

### Порядок реализации

1. **Добавить `GET /attempts/active`**— полностью самодостоятельный, не ломает ничего
2. **Добавить `GET /attempts`** — аналогично
3. **Расширить `finish` чтобы принимал body** или добавить `bulk-answers`— маленькое изменение
4. **Добавить `PATCH /users/me`** — новый router
5. **Добавить `GET /stats/calendar`** — новый endpoint в router stats
6. **Добавить `author_id` в catalog** — small change to existing code
7. **Share links** — last, separate feature branch

### Тестирование каждого

После каждого endpoint'а:
- `uv run python -m app.scripts.export_openapi --out ../frontend/src/shared/api/openapi.json`
- `cd ../frontend && bunx @hey-api/openapi-ts -i ...`
- `npx vite build` в frontend — должно проходить
- `uv run alembic revision --autogenerate` если новые таблицы
- `uv run pytest` — проверить что старые тесты не сломались

### Референсные файлы

Все endpoint'ы и схемы должны следовать существующим паттернам:
- `/backend/app/api/v1/tests.py` — пример CRUD router
- `/backend/app/services/test_service.py` — пример service layer
- `/backend/app/schemas/test_constructor.py` — пример schemas
- `/backend/app/repositories/base.py` — пример Repository pattern
- `/backend/app/api/errors.py` — пример error handling
