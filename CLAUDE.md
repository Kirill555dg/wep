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

## Protocol Buffers
- Follow official protobuf compatibility rules.
- Document every new field:
    ```
    // Show whether input spec is inconsistent
    bool spec_inconsistency = 11;
    ```

## Imports
- Import entire modules, not individual symbols.
- Group imports:
    1. Standard library/contrib: `import ...`
    2. Internal modules: `from ... import ...`
- Sort alphabetically within groups.
- Use consistent aliases: `import typing as tp`

Example:
```py
import logging

from echo.pylib import execution_info as ei
from echo.pylib import storage
from tasklet.sdk.v2 import python as sdk
```

## Logging
- Create module-level logger.
- Use f-strings with backticks for values.
- Log at `info` level or higher.
- Balance log volume between debugability and disk usage.

Example:
```py
import logging

LOGGER = logging.getLogger(__name__)
LOGGER.info(f"Running MR binary: `{path}`")
```

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
- Copy-paste safe code output.

---

# Project: Web Education Platform (WEP)

LMS-система для управления учебным процессом: классы, уроки, домашние задания, тестирование, статистика.

## Commands

### Infrastructure (PostgreSQL + Redis)
```bash
cd deploy && docker-compose up -d
```

### Backend
```bash
cd backend
source .venv/bin/activate
alembic upgrade head                                     # apply migrations
uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload
```
API docs: http://localhost:8023/api/docs

### Frontend
```bash
cd frontend
pnpm install
pnpm dev          # http://localhost:5173
pnpm build
pnpm test         # vitest unit tests (run once)
pnpm test:watch   # vitest watch mode
pnpm test:e2e     # cypress e2e (requires dev server)
```

### Linting / type-checking (backend)
```bash
cd backend
ruff check app/
mypy app/
```

---

## Architecture

### Backend - Clean Architecture (`backend/app/`)

```
api/v1/        - HTTP endpoints (thin: validate input, call service, map errors)
services/      - Business logic; raise ServiceError with a code string on domain errors
repositories/  - SQLAlchemy async data access, one file per aggregate
models/        - SQLAlchemy ORM models
schemas/       - Pydantic request/response models
realtime/      - WebSocket chat (ConnectionManager + Redis Pub/Sub broker)
core/          - Config (pydantic-settings), security (JWT/argon2), logging
db/            - Async session factory
```

Error flow: `services/exceptions.py::ServiceError` -> `api/errors.py` handler -> HTTP response.

Auth: JWT Bearer tokens. `api/dependencies.py::get_current_user` injects the authenticated user into endpoints.

### Frontend - Feature-Sliced Design (`frontend/src/`)

```
app/           - Bootstrap, router (React Router v6), role/auth guards
pages/         - Route-level components
widgets/       - Composite blocks (Header, Footer, MainLayout)
features/      - User scenarios (auth, join-class, notifications, profile)
entities/      - Domain models + Zustand stores (user, class, notification, student, teacher)
shared/        - axios instance, Radix/shadcn UI primitives, hooks, utils
```

API switching: each feature has `api/api.ts` (interface) + `api/api-real.ts` + `api/api-mock.ts`. The active impl is set at bootstrap; swap via `setAuthApi(impl)` / equivalent pattern.

State: Zustand stores per entity. React Query (`@tanstack/react-query` v4) for server state in features.

Roles: users have `student` / `teacher` role; `RoleProtectedRoute` guards role-specific pages. `MainRedirect` routes to `/student` or `/teacher` based on active role.

### Realtime
WebSocket chat with multi-instance fanout via Redis Pub/Sub (`realtime/redis_pubsub.py`). Redis is optional - single-instance mode works without it. Presence and typing indicators tracked in Redis with TTL.

### Infrastructure
`deploy/docker-compose.yml` runs PostgreSQL 16 and Redis 7. Backend and frontend run locally (not containerised yet).
