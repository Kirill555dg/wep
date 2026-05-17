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

## Dev Server

```bash
cd frontend
bun run dev
# open http://localhost:5173
```
