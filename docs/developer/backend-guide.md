# Backend - руководство разработчика

Детальное руководство по разработке серверной части WEP.

## Требования

- Python 3.12+
- PostgreSQL 16
- Redis 7 (опционально, для realtime чата)

## Установка окружения

### Python

#### macOS (Homebrew):
```bash
brew install python@3.12
```

#### macOS/Linux (pyenv - рекомендуется):
```bash
# Установка pyenv
curl https://pyenv.run | bash

# Перезапуск терминала
source ~/.zshrc  # для zsh
source ~/.bashrc # для bash

# Установка Python
pyenv install 3.12
pyenv local 3.12
```

#### Проверка:
```bash
python --version  # >= 3.12
```

### PostgreSQL

#### macOS (Homebrew):
```bash
brew install postgresql@16
brew services start postgresql@16
```

#### Создание БД:
```bash
createdb wep_education
createuser wep_user
psql -c "ALTER USER wep_user WITH PASSWORD 'wep_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE wep_education TO wep_user;"
```

### Redis (опционально)

#### macOS (Homebrew):
```bash
brew install redis
brew services start redis
```

## Установка проекта

```bash
cd backend

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

# Установить зависимости
pip install -r requirements.txt

# Настроить окружение
cp .env.example .env
# Отредактировать DATABASE_URL и другие параметры
```

## Запуск

### Миграции

```bash
# Применить миграции
alembic upgrade head

# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Откатить миграцию
alembic downgrade -1
```

### Development сервер

```bash
# С hot-reload
uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload

# Или через Makefile
make dev
```

### Через Docker

```bash
docker build -t wep-backend .
docker run -p 8023:8023 wep-backend
```

## Тестирование

```bash
# Запуск тестов
pytest

# С coverage
pytest --cov=app --cov-report=html

# Конкретный файл
pytest tests/test_auth.py

# С verbose
pytest -v
```

## Структура проекта (Clean Architecture)

```
backend/
├── app/
│   ├── main.py              # Entry point
│   ├── api/                 # API Layer
│   │   ├── v1/             # Endpoints
│   │   ├── dependencies.py  # DI, AuthZ
│   │   └── middleware/     # CORS, request_id
│   ├── services/            # Service Layer (business logic)
│   │   ├── auth.py
│   │   ├── classroom.py
│   │   ├── homework.py
│   │   └── ...
│   ├── repositories/        # Repository Layer (data access)
│   │   ├── base.py
│   │   ├── user.py
│   │   └── ...
│   ├── models/              # ORM Models
│   │   ├── users.py
│   │   ├── classes.py
│   │   └── ...
│   ├── schemas/             # Pydantic DTO
│   │   ├── users.py
│   │   ├── classrooms.py
│   │   └── ...
│   ├── core/                # Infrastructure
│   │   ├── config.py       # Configuration
│   │   ├── security.py     # JWT, Argon2
│   │   └── pagination.py
│   ├── db/                  # Database
│   │   └── session.py      # AsyncSession
│   └── realtime/            # WebSocket, Redis
│       ├── connection_manager.py
│       └── redis_pubsub.py
├── alembic/                 # Migrations
├── tests/                   # Tests
├── requirements.txt
├── Dockerfile
└── Makefile
```

## Слои Clean Architecture

1. **API Layer** (`app/api/`)
   - HTTP/WebSocket endpoints
   - Валидация входных данных
   - Зависимости через DI
   - Вызов сервисов

2. **Service Layer** (`app/services/`)
   - Бизнес-логика use-cases
   - Проверка прав доступа
   - Оркестрация репозиториев
   - Не содержит SQL

3. **Repository Layer** (`app/repositories/`)
   - CRUD операции
   - SQLAlchemy запросы
   - Изоляция SQL от бизнес-логики

4. **Models** (`app/models/`)
   - SQLAlchemy ORM модели
   - Таблицы и связи

**Правило зависимостей**: внешние слои зависят от внутренних, но не наоборот.

## Добавление нового endpoint

### 1. Создать DTO схемы

```python
# app/schemas/homework.py
from pydantic import BaseModel
from uuid import UUID

class HomeworkCreate(BaseModel):
    lesson_id: UUID
    title: str
    description: str

class HomeworkResponse(BaseModel):
    id: UUID
    lesson_id: UUID
    title: str
    description: str
```

### 2. Создать/обновить модель

```python
# app/models/homework.py
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base

class Homework(Base):
    __tablename__ = "homework"
    
    id = Column(UUID, primary_key=True)
    lesson_id = Column(UUID, ForeignKey("lessons.id"))
    title = Column(String, nullable=False)
    description = Column(String)
```

### 3. Создать/обновить репозиторий

```python
# app/repositories/homework.py
from app.repositories.base import BaseRepository
from app.models.homework import Homework

class HomeworkRepository(BaseRepository[Homework]):
    def __init__(self, session):
        super().__init__(session, Homework)
```

### 4. Создать/обновить сервис

```python
# app/services/homework.py
from app.repositories.homework import HomeworkRepository
from app.schemas.homework import HomeworkCreate, HomeworkResponse

class HomeworkService:
    def __init__(self, homework_repo: HomeworkRepository):
        self.homework_repo = homework_repo
    
    async def create_homework(self, data: HomeworkCreate) -> HomeworkResponse:
        # Бизнес-логика
        homework = await self.homework_repo.create(data.dict())
        return HomeworkResponse.from_orm(homework)
```

### 5. Создать endpoint

```python
# app/api/v1/homework.py
from fastapi import APIRouter, Depends
from app.schemas.homework import HomeworkCreate, HomeworkResponse
from app.services.homework import HomeworkService
from app.api.dependencies import get_homework_service

router = APIRouter(prefix="/homework", tags=["homework"])

@router.post("/", response_model=HomeworkResponse)
async def create_homework(
    data: HomeworkCreate,
    service: HomeworkService = Depends(get_homework_service)
):
    return await service.create_homework(data)
```

### 6. Добавить в роутер

```python
# app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1 import homework

api_router = APIRouter()
api_router.include_router(homework.router)
```

## Работа с БД

### AsyncSession

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session

async def some_function(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Транзакции

```python
async with session.begin():
    user = await user_repo.create(data)
    profile = await profile_repo.create(user_id=user.id)
    # Автоматический commit при выходе из блока
```

## Аутентификация и авторизация

### JWT токены

```python
from app.core.security import create_access_token

token = create_access_token(
    data={"sub": str(user.id), "role": user.role}
)
```

### Защита endpoints

```python
from app.api.dependencies import get_current_user, get_current_teacher

@router.get("/me")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/classrooms")
async def create_classroom(
    data: ClassroomCreate,
    teacher: Teacher = Depends(get_current_teacher)
):
    # Только для teacher
    ...
```

## WebSocket (Realtime чат)

### Connection Manager

```python
from app.realtime.connection_manager import ConnectionManager

manager = ConnectionManager()

@router.websocket("/ws/{classroom_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    classroom_id: UUID
):
    await manager.connect(classroom_id, websocket)
    try:
        while True:
            message = await websocket.receive_text()
            await manager.broadcast(classroom_id, message)
    except WebSocketDisconnect:
        manager.disconnect(classroom_id, websocket)
```

## Конфигурация

### Переменные окружения

Все настройки в `app/core/config.py`:

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## Линтинг и форматирование

### Ruff

```bash
# Проверка
ruff check app tests

# Форматирование
ruff format app tests
```

### Mypy

```bash
mypy app
```

## Частые команды (Makefile)

```bash
# Установка зависимостей
make install

# Линтинг
make lint

# Форматирование
make format

# Проверка типов
make type

# Тесты
make test

# Запуск dev-сервера
make dev

# Миграции
make migrate

# Очистка
make clean
```

## API документация

После запуска сервера:

- **Swagger UI**: http://localhost:8023/api/docs
- **ReDoc**: http://localhost:8023/api/redoc
- **OpenAPI JSON**: http://localhost:8023/api/openapi.json

## Экспорт OpenAPI для frontend

```bash
# Экспортировать контракт для frontend
python -m app.scripts.export_openapi --out ../frontend/src/shared/api/openapi.json
```

## Соглашения

### Именование

- Models: `PascalCase` (User, Classroom)
- Функции: `snake_case` (create_user, get_classrooms)
- Переменные: `snake_case` (user_id, classroom_data)
- Constants: `UPPER_SNAKE_CASE` (MAX_LIMIT, API_V1_PREFIX)

### Imports

```python
# Stdlib
from typing import List, Optional
from uuid import UUID

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy import select

# Local
from app.models.users import User
from app.schemas.users import UserResponse
from app.services.auth import AuthService
```

### Async/Await

Все DB операции асинхронные:

```python
async def get_user(user_id: UUID) -> User:
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()
```

## Отладка

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Breakpoints

```python
import pdb; pdb.set_trace()
# или
breakpoint()
```

### SQL logging

В `.env`:
```
DEBUG=True
```

SQLAlchemy будет логировать все запросы.

## Полезные ссылки

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2](https://docs.pydantic.dev/latest/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pytest](https://docs.pytest.org/)
