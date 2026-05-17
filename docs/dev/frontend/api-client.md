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

## Tech Stack

- React 18 + TypeScript + Vite
- Bun (package manager & runner)
- TanStack Query (v4) for server state
- Zustand for local client state
- react-router-dom for routing
- Tailwind CSS + Radix UI (shadcn) for UI
- typst.ts for rich content rendering
- orval (codegen from OpenAPI)

## FSD Structure

See source tree under `frontend/src/`.

| Layer | Purpose |
|-------|---------|
| app | Entry point, routing, providers |
| pages | Route-level pages |
| widgets | Composite UI blocks |
| features | User scenarios (auth, test mgmt, taking, search, upload) |
| entities | Domain models & stores (user, test, question, attempt) |
| shared | Reusable primitives (api, ui, lib, hooks) |
