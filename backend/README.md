# WEP Backend

FastAPI backend для Web Education Platform.

## Технологии

- Python 3.12+
- FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic (миграции)

## Архитектура

Clean Architecture:
- API Layer (endpoints)
- Service Layer (business logic)
- Repository Layer (data access)
- Models (ORM)

## Установка

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate    # Windows

pip install -r requirements.txt

cp .env.example .env
# Отредактировать .env

alembic upgrade head

uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload
```

## API документация

- Swagger UI: http://localhost:8023/api/docs
- OpenAPI JSON: http://localhost:8023/api/openapi.json
