# Frontend Development Notes

## API Client Generation

The frontend consumes a FastAPI backend. OpenAPI schema is exported from the backend and used to generate the TypeScript HTTP client.

### Exporting OpenAPI Schema

Run from repository root:

```bash
PYTHONPATH=backend backend/.venv/bin/python -m app.scripts.export_openapi --out frontend/src/shared/api/openapi.json
```

This writes `openapi.json` which is then used by the code generator.

### Generating The Client

> TODO after selecting generator tool (orval / @hey-api/openapi-ts)

## Tech Stack

- React 18 + TypeScript + Vite
- TanStack Query (v4) for server state
- Zustand for local client state
- react-router-dom for routing
- Tailwind CSS + Radix UI (shadcn) for UI
- typst.ts for rich content rendering
