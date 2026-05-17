# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Development Rules

## General Principles
- Think before coding. Read existing files first.
- Prefer editing over rewriting entire files.
- Skip files >100KB unless required.
- Test code before completion.
- Keep solutions simple and direct.
- User instructions override all rules.

## Output Format
- Code first, explanation only if non-obvious.
- Minimal comments - only for unclear logic.
- No boilerplate unless requested.

## Code Rules
- Simplest working solution. No over-engineering.
- No abstractions for single-use operations.
- Read files before modifying. Never edit blind.
- No docstrings/type annotations on unchanged code.
- No error handling for impossible scenarios.
- Three similar lines > premature abstraction.
- Define all constants as variables, never use magic values/literals.

## API & Database
- External-facing IDs must be strings (even if numeric internally).
- Database access only through SQLAlchemy.

## Imports
- Import entire modules, not individual symbols.
- Group imports:
    1. Standard library/contrib: `import X.Y as alias`
    2. Internal modules: `from app.X import module`
- Sort alphabetically within groups.

Example:
```py
import sqlalchemy as sa
import sqlalchemy.orm as sqla_orm

from app.models import test_constructor as tc_models
from app.schemas import test_constructor as tc_schemas
```

## Logging
- Create module-level logger.
- Use f-strings with backticks for values.
- Log at `info` level or higher.

## Code Review
- State bug, show fix, stop.
- No scope creep or compliments.

## Debugging
- Never speculate without reading code first.
- State findings, location, and fix in one pass.
- If cause unclear: say so, don't guess.

## Formatting
- Plain text only: hyphens, straight quotes.
- No decorative symbols.

---

# Project: Интерактивный конструктор образовательных тестов

Курсовая | Миркин К.Л. | ИКБО-10-23 | Срок: 18.05.2026

Полная документация: `docs/developer/backend-guide.md`

## Quick reference

### Infrastructure
```bash
cd deploy && docker-compose up -d
```

### Backend (all commands via uv)
```bash
cd backend
uv pip install -r requirements.txt -r requirements-dev.txt
uv run alembic upgrade head
uv run uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload
```

### Tests
```bash
uv run pytest tests/ --ignore=tests/fuzz   # service + HTTP
uv run pytest tests/fuzz/                  # fuzzing (Hypothesis)
uv run pytest tests/ -k "name"             # single test
```

### Smoke test (works in production)
```bash
python tools/smoke_test.py
```

### Lint
```bash
uv run ruff check app/
```

## Architecture summary

```
api/v1/     → validate, call service, map errors
services/   → business logic, raise ServiceError
repos/      → SQLAlchemy async queries
models/     → ORM (test_constructor.py, users.py)
schemas/    → Pydantic DTOs (Create / Update / Response)
core/       → config, JWT/argon2, MinIO client
```

DB error classification (`api/errors.py`):
- SQLSTATE 22xxx / 23xxx (bad input) → 422
- Other DB errors → 500

Test isolation: every test function gets a fresh PostgreSQL schema (UUID), dropped on teardown. `http_client` fixture overrides `get_db` with per-request sessions.

Fuzz tests in `tests/fuzz/` — invariant: API never returns 500.

Coursework report: `coursework/main.typ`.
