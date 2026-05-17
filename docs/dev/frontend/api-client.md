# Frontend Development Notes

## Package Manager

All frontend commands use **Bun**.

```bash
bun install          # install dependencies
bun add <pkg>        # add runtime dependency
bun add -d <pkg>     # add dev dependency
bunx <bin>           # run package binary
bun dev              # start Vite dev server
bun build            # production build
bun test             # run Vitest
```

## API Client Generation

The frontend consumes a FastAPI backend. OpenAPI schema is exported from the backend and used to generate the TypeScript HTTP client.

### 1. Export OpenAPI Schema

Run from repository root:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m app.scripts.export_openapi --out frontend/src/shared/api/openapi.json
```

### 2. Generate Client

```bash
cd frontend
bunx orval --config orval.config.js
```

This creates typed Axios functions and TanStack Query hooks under `src/shared/api/client/`.

## Typst Rendering

Primary renderer is `@myriaddreamin/typst.ts` (WASM).  
Due to a Vite/Rollup build issue with the WASM bundle, a lightweight **fallback** is currently active:
it renders Typst source as formatted HTML (`**bold**, $math$, lists`).

To switch back to full WASM:
1. Update `src/shared/lib/typst.ts` to import from `@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs`.
2. Ensure `vite.config.ts` marks the WASM bundle as asset or external.

## Tech Stack

- React 18 + TypeScript + Vite
- Bun (package manager & runner)
- TanStack Query (v4) for server state
- Zustand for local client state
- react-router-dom for routing
- Tailwind CSS + Radix UI (shadcn) for UI
- typst.ts (WASM/fallback) for rich content rendering
- orval (codegen from OpenAPI)
- axios (with JWT interceptor)

## FSD Structure

| Layer | Purpose |
|-------|---------|
| app | Entry point, routing, providers, auth guard |
| pages | Route-level pages: catalog, editor, take-test, results, login, register, profile, stats |
| widgets | TestCard, QuestionEditor, SearchBar, TagInput, ResultsPanel, MainLayout |
| features | Auth, TestManagement, Catalog, TestTaking, MediaUpload, TypstPreview |
| entities | User, Test, Question, Attempt stores (Zustand) |
| shared | HTTP client, UI primitives, helpers, toast, format-score |

## Typst Rendering

Primary renderer is `@myriaddreamin/typst.ts` WASM, bundled by Vite via `vite-plugin-wasm`.
Fonts are fetched automatically from CDN. No manual WASM copying required.

## Dev Server

Local development uses the native Bun + Vite dev server. Backend runs in Docker (see below).

```bash
cd frontend
bun run dev
# open http://localhost:5173
# API requests are proxied to localhost:8023 (Vite proxy in vite.config.ts)
```

## Deployment

### Development (local)

Backend and database run in Docker. Frontend runs natively with Bun for HMR.

```bash
# Terminal 1 — infrastructure + backend
cd deploy
cp .env.example .env
docker compose up -d   # postgres, minio, backend

# Terminal 2 — frontend (requires Bun installed locally)
cd frontend
cp .env.example .env
bun install
bun run dev
```

### Production (VPS)

Everything runs in Docker via the production overlay.

```bash
cd deploy
cp .env.prod.example .env
# edit .env — set real secrets, domain, MinIO_PUBLIC_URL
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Services exposed:
- `http://your-domain` — frontend (nginx static) + API proxy
- `https://your-domain:9000` — MinIO (object storage, direct access)

## CI/CD

GitHub Actions builds and pushes Docker images on every push to `prksp_coursework`.

### Required Repository Secrets

| Secret | How to get |
|--------|------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token (or password) |
| `TELEGRAM_BOT_TOKEN` | Create bot via @BotFather, copy token |
| `TELEGRAM_CHAT_ID` | Open chat with bot, call `https://api.telegram.org/bot<TOKEN>/getUpdates`, find `message.chat.id` |

Add secrets in GitHub: *Settings → Secrets and variables → Actions → New repository secret*.

### Docker Images

| Image | Dockerfile | Tag |
|-------|-----------|-----|
| Backend | `backend/Dockerfile` | `<dockerhub-user>/test-constructor-backend:latest` |
| Frontend | `frontend/Dockerfile.prod` | `<dockerhub-user>/test-constructor-frontend:latest` |

### Manual push (without CI)

```bash
docker login
cd backend && docker build -t <dockerhub-user>/test-constructor-backend:latest . && docker push <dockerhub-user>/test-constructor-backend:latest
cd ../frontend && docker build -f Dockerfile.prod -t <dockerhub-user>/test-constructor-frontend:latest . && docker push <dockerhub-user>/test-constructor-frontend:latest
```

### Health Checks

- Backend health: HTTP GET `/api/v1/health` — used by Docker Compose `healthcheck`
- Frontend health: HTTP GET `/` — returns 200 when nginx serves static SPA

## Docker Compose Files

| File | Purpose |
|------|---------|
| `deploy/docker-compose.yml` | Base: postgres, minio, backend |
| `deploy/docker-compose.prod.yml` | Overlay: adds frontend (nginx static) on port 80 |
| `frontend/Dockerfile.dev` | Image with Bun for `bun run dev` (not used in compose) |
| `frontend/Dockerfile.prod` | Multi-stage: Bun build → `nginx:alpine` |
| `frontend/nginx-prod.conf` | SPA fallback + proxy `/api/` to backend |

## Build

```bash
cd frontend
bun run build
```

Produces `dist/` with static files + WASM chunks (28 MB compiler, 1 MB renderer).
