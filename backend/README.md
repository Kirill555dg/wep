# WEP Backend

FastAPI backend (Clean Architecture: API → Service → Repository → ORM).

**Стек:** Python 3.12+, FastAPI, SQLAlchemy (async), Alembic, PostgreSQL, MinIO, uv.

## Быстрый старт

```bash
cd backend
cp .env.example .env
uv venv && uv pip install -r requirements.txt -r requirements-dev.txt
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8023
```

## Документация

- [Backend — документация](../docs/dev/backend/)
- [Быстрый старт окружения](../docs/dev/getting-started.md)
- Swagger: http://localhost:8023/api/docs
