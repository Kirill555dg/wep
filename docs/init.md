# WEP Project — Full Context Snapshot

Last updated: 2026-05-18
Branch: `prksp_coursework`
Commit: `ef2e1f6`

## One-sentence summary

Web Education Platform — интерактивный конструктор образовательных тестов с поддержкой Typst-формул, медиа и автопроверкой. Backend на FastAPI + PostgreSQL. Frontend на React + Tailwind + shadcn/ui.

## Architecture (высокий уровень)

```
┌──────────────────────────────────────────────────────────────┐
│  Client (React 18 + Vite + Tailwind + shadcn/ui)            │
│  ├── Pages: Catalog, Test View, Take/Edit, History, Profile  │
│  ├── Unified API: @hey-api/openapi-ts (auto-generated)       │
│  └── State: Zustand (client) + TanStack Query (server)       │
├──────────────────────────────────────────────────────────────┤
│  Server (FastAPI + PostgreSQL + MinIO)                       │
│  ├── Clean Architecture: API → Service → Repository → Models  │
│  ├── Auth: JWT (HS256) + Argon2id                            │
│  └── File storage: MinIO (S3-compatible)                     │
└──────────────────────────────────────────────────────────────┘
```

---

## Backend — что есть и чего нет

### Что есть (28 endpoints)

| Area | Endpoints | Status |
|---|---|---|
| Health | `GET /`, `/health`, `/ping` | ✅ |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` | ✅ |
| Tests | CRUD + questions CRUD (5 ops + 3 sub-ops) | ✅ |
| Catalog | Search (`q`, `tags`), get public test | ✅ |
| Tags | List, create | ✅ |
| Attempts | Start, get, submit single answer, finish, get result | ✅ |
| Stats | Author stats, per-test stats | ✅ |
| Media | Upload to MinIO | ✅ |

### Чего нет (7 gaps)

| # | Endpoint | Why | Priority |
|---|---|---|---|
| 1 | `GET /attempts` (list user's attempts) | History page | 🔴 P0 |
| 2 | `GET /attempts/active` (check active attempt) | Test View CTA (Start/Continue) | 🔴 P0 |
| 3 | `POST /attempts/{id}/bulk-answers` | Submit all answers at once before finish | 🟡 P1 |
| 4 | `GET /stats/calendar` | Activity calendar (GitHub heatmap) | 🟡 P1 |
| 5 | `PATCH /users/me` | Update profile (avatar, name, etc.) | 🟡 P1 |
| 6 | `author_id` in catalog params | Filter by author | 🟢 P2 |
| 7 | Share links (one-time) | Private test sharing | 🟢 P2 |

Full details: `/docs/backend-todo.md`

---

## Frontend — что есть и чего нет

### Что есть (shared infra)

| Component | Path | Status |
|---|---|---|
| TopBar | `src/widgets/top-bar/TopBar.tsx` | ✅ Thin 48px sticky bar |
| Router | `src/app/router.tsx` | ✅ 12 routes defined |
| API client | `src/shared/api/index.ts` | ✅ Unified @hey-api exports |
| Auth hook | `src/shared/hooks/useAuth.ts` | ✅ Guard + redirect |
| Attempt cache | `src/shared/hooks/useAttemptCache.ts` | ✅ localStorage persistence |
| API query/mutation | `src/shared/hooks/useApi.ts` | ✅ TanStack wrappers |
| Error handler | `src/shared/lib/api-error.ts` | ✅ Extract code + message |
| Build | — | ✅ `npx vite build` passes (1.3s) |

### Pages (все — placeholders unless marked ✅)

| # | Page | Route | Status | Island |
|---|---|---|---|---|
| 1 | Catalog | `/catalog` | 🔄 Skeleton (needs full impl) | ISLAND-1 |
| 2 | Login | `/login` | ✅ Functional (needs react-hook-form refactor) | ISLAND-2 |
| 3 | Register | `/register` | ✅ Functional (needs react-hook-form refactor) | ISLAND-2 |
| 4 | Test View | `/tests/:testId` | 🔄 Skeleton | ISLAND-3 |
| 5 | Take Test | `/tests/:testId/take` | 🔄 Skeleton | ISLAND-4 |
| 6 | Edit Test | `/tests/:testId/edit` | 🔄 Skeleton (reuse ISLAND-4) | ISLAND-4 |
| 7 | History | `/history` | 🔄 Skeleton | ISLAND-6 |
| 8 | My Tests | `/my-tests` | 🔄 Skeleton | ISLAND-7 |
| 9 | Results | `/attempts/:attemptId` | 🔄 Skeleton | ISLAND-5 |
| 10 | Profile | `/profile` | ✅ Functional (needs simplification) | ISLAND-8 |

### Чего нет (компоненты)

| Component | Needed by | Status |
|---|---|---|
| TypstRender | ISLAND-4 (core) | ❌ Not built yet |
| MediaCarousel | ISLAND-4 | ❌ Not built yet |
| AnswerBlocks (single/multiple/text/file) | ISLAND-4 | ❌ Not built yet |
| QuestionPanel (240px side) | ISLAND-4, ISLAND-5 | ❌ Not built yet |
| TypstEditorPage (split pane) | ISLAND-4 (sub-page) | ❌ Not built yet |
| CompletionScreenOverlay | ISLAND-5 | ❌ Not built yet |
| ActivityCalendar | ISLAND-6 | ❌ Not built yet |

---

## Database schema (PostgreSQL)

Tables: `users`, `login_data`, `tests`, `questions`, `options`, `tags`, `test_tags`, `attempts`, `answers`

Latest migration: `alembic/versions/20260518_0250-d82fa57d2ce6_init.py`

New columns (vs original):
- `tests.attempt_limit: int | None`
- `tests.track_time: bool`
- `tests.completion_message: str | None`

---

## Key decisions (decision log)

| Date | Decision | Rationale |
|---|---|---|
| 2026-05-18 | Backend: `attempt_limit` → `Optional[int]` (None = unlimited, 1 = single) | User request: explicit "None is literal unlimited" |
| 2026-05-18 | Frontend: No manual zoom UI for Typst | User request: native browser scaling only (Ctrl ±) |
| 2026-05-18 | Frontend: `attempt_limit` UI → simple number input + `∞` icon button | User request: no dropdown, just icon + tooltip |
| 2026-05-18 | Frontend: Resume is default behavior, not toggle | User request: always allow resume |
| 2026-05-18 | Frontend: Shared UI kit — shadcn/ui + lucide-react only | No new deps, compose from primitives + Tailwind |
| 2026-05-18 | Frontend: Shared API — @hey-api/openapi-ts only | Orval-generated code removed, old clients removed |
| 2026-05-18 | Frontend: TopBar replaces Header+Footer | Minimal 48px sticky, no footer |

---

## File structure (what matters)

```
wep/
├── backend/                    — FastAPI server
│   ├── app/
│   │   ├── api/v1/            — All routers (auth, tests, catalog, attempts, stats, media)
│   │   ├── core/config.py      — Settings (DB URL: localhost:5433)
│   │   ├── models/            — SQLAlchemy models
│   │   ├── schemas/           — Pydantic schemas
│   │   ├── repositories/      — Repository pattern
│   │   └── services/          — Business logic
│   ├── alembic/versions/       — Migrations (latest: 20260518_0250_init.py)
│   └── .env                    — DATABASE_URL=postgresql://...:5433/...
│
├── frontend/                   — React 18 + Vite
│   ├── src/
│   │   ├── app/               — router.tsx, providers.tsx, guards/
│   │   ├── pages/             — All 10 page components (some skeleton, some functional)
│   │   ├── widgets/           — top-bar/ (only surviving widget)
│   │   ├── features/          — auth/, stats/, render/, upload/ (legacy; some active)
│   │   ├── entities/          — user/, attempt/ (stores)
│   │   ├── shared/            — api/, ui/, hooks/, lib/, styles/
│   │   └── main.tsx           — Entry (Providers + TopBar + Router)
│   ├── docs/agents/           — Subagent task manifest + 9 island files
│   ├── package.json           — bun deps (react 18, tailwind, shadcn/ui, zustand, tanstack)
│   └── vite.config.ts         — Proxy /api → localhost:8023
│
├── deploy/                    — docker-compose.yml (postgres 5433, minio 9000, backend 8023)
├── docs/
│   ├── dev/frontend/          — 11 design docs (01-layout … 11-backend-deps)
│   └── backend-todo.md        — 7 missing backend endpoints (full specs)
└── AGENTS.md                  — Tooling rules (uv for backend, bun for frontend)
```

---

## Quick commands

| What | Command |
|---|---|
| Backend check imports | `cd backend && uv run python -c "from app.main import app; print('OK')"` |
| Backend export OpenAPI | `cd backend && uv run python -m app.scripts.export_openapi --out ../frontend/src/shared/api/openapi.json` |
| Regenerate frontend API | `cd frontend && bunx @hey-api/openapi-ts -i ./src/shared/api/openapi.json -o ./src/shared/api/generated` |
| Frontend build | `cd frontend && npx vite build` |
| Run tests | `cd frontend && npx vitest run` |
| Docker (Postgres + MinIO) | `cd deploy && docker-compose up -d postgres minio` |
| Alembic migrate | `cd backend && uv run alembic upgrade head` |
| Alembic generate | `cd backend && uv run alembic revision --autogenerate -m "msg"` |

---

## Decision needed

### Первоочерядно — что делаем дальше?

**Option A: Finish backend gaps**
- Implement `GET /attempts` + `GET /attempts/active` + `POST /attempts/{id}/bulk-answers`
- These are 🔴 P0 blockers for frontend islands 3, 4, 5, 6

**Option B: Build frontend islands (parallel)**
- Islands 1 (Catalog) and 2 (Auth) are independent of missing backend
- They only need already-working endpoints (`GET /catalog`, `POST /auth/login`)

**Option C: Parallel work**
- I work on frontend (Catalog + Auth)
- You (or another agent) works on backend (P0 endpoints)

**Recommended: C** → Backend P0 + Frontend ISLAND-1 in parallel. Backend P1 endpoints can wait.

---

## If lost, read these first

| If you need to understand… | Read this |
|---|---|
| Page layout, navigation | `docs/dev/frontend/01-layout.md` |
| Catalog design | `docs/dev/frontend/02-catalog.md` |
| Test taking / editing template | `docs/dev/frontend/06-test-content-template.md` |
| Backend gaps | `docs/backend-todo.md` |
| Subagent tasks | `frontend/docs/agents/MANIFEST.md` + `ISLAND-*.md` |
| Backend architecture | `backend/app/api/v1/*.py` + `services/*.py` |
| API schema | `frontend/src/shared/api/openapi.json` |
| Current DB schema | `backend/alembic/versions/20260518_0250-d82fa57d2ce6_init.py` |

---

*Rebuild this file whenever major state changes.*
