# Backend — руководство разработчика

Серверная часть реализует REST API для интерактивного конструктора образовательных тестов.
Стек: Python 3.12, FastAPI, PostgreSQL 16, MinIO, SQLAlchemy (async), Alembic, uv.

---

## Быстрый старт

### Предварительные требования

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — установка: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Docker + Compose (Colima на macOS: `brew install colima && colima start`)

### Инфраструктура (PostgreSQL + MinIO)

```bash
cd deploy
docker-compose up -d postgres minio
```

MinIO console: http://localhost:9001 (minioadmin / minioadmin)

### Установка зависимостей

```bash
cd backend

# Рабочая среда: создать venv и установить runtime + dev зависимости
uv venv
uv pip install -r requirements.txt -r requirements-dev.txt

# В Dockerfile и CI (только runtime):
# uv pip install --system -r requirements.txt
```

### Миграции и запуск

```bash
cd backend
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload
```

API docs: http://localhost:8023/api/docs

---

## Зависимости

| Файл | Назначение |
|------|-----------|
| `requirements.txt` | Runtime зависимости (попадают в Docker-образ) |
| `requirements-dev.txt` | Тестирование, линтинг (только локально / CI) |
| `.ruff.toml` | Настройки ruff |
| `mypy.ini` | Настройки mypy |
| `pytest.ini` | Настройки pytest |

Добавить runtime-зависимость → `requirements.txt`. Dev-only → `requirements-dev.txt`.

---

## Структура проекта

```
backend/
├── app/
│   ├── main.py                   # Lifespan, ASGI app, middleware
│   ├── api/
│   │   ├── v1/                   # HTTP-обработчики по ресурсам
│   │   │   ├── auth.py           # /auth/
│   │   │   ├── tests.py          # /tests/
│   │   │   ├── catalog.py        # /catalog/
│   │   │   ├── attempts.py       # /attempts/
│   │   │   ├── stats.py          # /stats/
│   │   │   ├── media.py          # /media/
│   │   │   └── tags.py           # /tags/
│   │   ├── dependencies.py       # get_current_user (JWT → User)
│   │   ├── errors.py             # Обработчики ServiceError, DBAPIError
│   │   └── middleware/
│   ├── services/
│   │   ├── auth.py               # Регистрация, аутентификация, роли
│   │   ├── test_service.py       # CRUD тестов и вопросов
│   │   ├── attempt_service.py    # Жизненный цикл попытки, проверка ответов
│   │   ├── catalog_service.py    # Публичный каталог, статистика автора
│   │   ├── grading.py            # Чистая логика оценивания (без БД)
│   │   ├── media_service.py      # Загрузка файлов в MinIO
│   │   └── exceptions.py         # ServiceError
│   ├── repositories/
│   │   ├── base.py               # BaseRepository[T] с CRUD
│   │   ├── user.py               # UserRepository, LoginDataRepository
│   │   └── test_constructor.py   # Test/Question/Tag/Attempt/Answer репозитории
│   ├── models/
│   │   ├── users.py              # User, LoginData, Teacher, Student
│   │   └── test_constructor.py   # Test, Question, Option, Tag, Attempt, Answer
│   ├── schemas/
│   │   ├── users.py              # UserCreate, UserResponse, TokenResponse, …
│   │   └── test_constructor.py   # TestCreate, QuestionCreate, AttemptResponse, …
│   ├── core/
│   │   ├── config.py             # Settings (pydantic-settings, читает .env)
│   │   ├── security.py           # JWT, Argon2id
│   │   └── minio_client.py       # MinIO singleton, ensure_bucket()
│   └── db/
│       ├── session.py            # AsyncEngine, AsyncSessionLocal, get_db()
│       └── url.py                # to_psycopg_url / to_asyncpg_url
├── alembic/versions/             # Миграции
├── tests/                        # Unit + сервисные + HTTP тесты
├── requirements.txt
├── requirements-dev.txt
├── .ruff.toml                   # Настройки ruff
├── mypy.ini                     # Настройки mypy
├── pytest.ini                   # Настройки pytest
└── Dockerfile
```

---

## Архитектурные правила

### Поток запроса

```
HTTP → api/v1/*.py (валидация)
     → services/*.py (бизнес-логика)
     → repositories/*.py (SQL)
     → PostgreSQL / MinIO
```

Обратные зависимости запрещены: репозиторий не знает об API.

### Обработка ошибок

```python
# Сервис → ServiceError
raise ServiceError("Test not found", code="test_not_found")

# Обработчик API → HTTPException
if exc.code == "test_not_found":
    raise http_errors.not_found("Test not found")
```

**DB-ошибки** (`api/errors.py::db_api_error_handler`):
- SQLSTATE `22xxx` (Data Exception: null bytes, overflow) → **422**
- SQLSTATE `23xxx` (Integrity Violation: дублирующий ключ) → **422**
- Прочие DB-ошибки (соединение, синтаксис) → **500**

Функции `_extract_sqlstate` и `_is_client_fault` содержат всю логику классификации.

### Импорты

```python
# contrib/stdlib: import X.Y as alias
import sqlalchemy as sa
import sqlalchemy.orm as sqla_orm
import sqlalchemy.ext.asyncio as sa_asyncio
import starlette.status as http_status

# internal: from app.X import module
from app.schemas import test_constructor as tc_schemas
from app.models import test_constructor as tc_models
from app.repositories import test_constructor as tc_repos
from app.services import exceptions as svc_exc
```

Никогда не импортируем отдельные символы (`from app.schemas.test_constructor import TestCreate`).

---

## Домен: Test Constructor

### Модель данных

```
User ──< Test ──< Question ──< Option
              └──< Attempt ──< Answer
Test ><── TestTag ><── Tag
```

Ключевые детали:
- `Question.correct_answer` — эталонный ответ для TEXT-вопросов
- `Question.explanation` — показывается после завершения попытки; используется как fallback correct_answer если `correct_answer = null`
- `Attempt`: частичный уникальный индекс `(user_id, test_id) WHERE status = 'IN_PROGRESS'` — предотвращает дублирующие активные попытки на уровне БД

### Оценивание

`GradingService` (без IO):
- `SINGLE_CHOICE` / `MULTIPLE_CHOICE`: проверяет точное совпадение множества ID
- `TEXT`: нормализованное сравнение без учёта регистра и пробелов
- `ESSAY`: всегда `(None, 0)` — ручная проверка

---

## Миграции

```bash
# Применить все
uv run alembic upgrade head

# Создать новую (autogenerate сравнивает модели с БД)
uv run alembic revision --autogenerate -m "add_X_to_Y"

# Откатить последнюю
uv run alembic downgrade -1
```

При изменении модели → новая миграция. Не редактировать существующие миграции после деплоя.

---

## Тестирование

### Запуск

```bash
# Требует запущенных PostgreSQL + MinIO
uv run pytest tests/ --ignore=tests/fuzz   # unit + сервисные + HTTP (~15s)
uv run pytest tests/fuzz/                  # Hypothesis fuzzing (~30s)
uv run pytest tests/ -k "login"            # один тест по имени
```

### Модель изоляции

Каждая тест-функция получает **свою PostgreSQL-схему** (UUID-именованную), созданную через DDL из ORM-метаданных и удалённую после завершения. Тесты никогда не загрязняют общую БД.

Два fixture'а (`conftest.py`):

| Fixture | Назначение | Используется в |
|---------|-----------|---------------|
| `db_session` | Одна `AsyncSession` в изолированной схеме | Сервисные тесты |
| `http_client` | `httpx.AsyncClient` + override `get_db` (новая сессия на каждый запрос) | HTTP-тесты, фаззинг |

### Структура тестов

```
tests/
├── conftest.py             # db_session, http_client fixtures
├── test_infra.py           # PostgreSQL + MinIO smoke tests
├── test_auth_service.py    # AuthService: регистрация, аутентификация
├── test_test_service.py    # TestService: CRUD тестов и вопросов
├── test_attempt_service.py # AttemptService: попытки, ответы, оценки
├── test_grading_service.py # GradingService (unit, без БД)
├── test_role_access.py     # HTTP: контроль доступа и ownership
├── test_token_role_mismatch.py
└── fuzz/
    ├── conftest.py
    └── test_fuzz_api.py    # Hypothesis: инвариант "никогда не 500"
```

### Фаззинг

Тесты в `tests/fuzz/` проверяют: для любого входного значения API возвращает `{200,201,400,401,403,404,409,422}`, но никогда `500`. Включают:
- Property-based тесты через Hypothesis (`@given`)
- Параметризованные SQL-injection / XSS паттерны
- Граничные значения (пустые строки, отрицательные лимиты)

Каждая тест-функция изолирована через `http_client` fixture.

---

## Деплой

### Локальный Docker Compose

```bash
cd deploy
docker-compose up -d           # PostgreSQL, MinIO
docker-compose up -d backend   # + backend (после сборки)
```

### Сборка образа

```bash
cd backend
docker build -t wep-backend .
```

Dockerfile использует `uv pip install --system` для установки зависимостей — тот же инструмент, что и при локальной разработке.

### Переменные окружения

Все параметры через переменные окружения. Пример в `backend/.env.example`:

```
DATABASE_URL=postgresql://wep_user:wep_password@localhost:5433/wep_education
SECRET_KEY=your-secret-key
MINIO_ENDPOINT=127.0.0.1:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=wep-media
```

---

## Линтинг и типизация

```bash
uv run ruff check app/         # линтинг
uv run ruff check app/ --fix   # автоисправление
uv run mypy app/               # проверка типов
```

Настройки в `.ruff.toml` (линтер) и `mypy.ini` (типизация).
