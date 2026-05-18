# WEP Frontend — Subagent Task Manifest

This directory contains standalone task descriptions for each functional "island"
of the WEP (Web Education Platform) frontend. Every `.md` file is self-contained
and gives a single subagent everything it needs to implement one island.

## Islands (order matters)

| # | Island | File | Status | Depends on |
|---|---|---|---|---|
| 0 | Shared infra | [ISLAND-0-shared.md](ISLAND-0-shared.md) | ✅ Done | None |
| 1 | Catalog | [ISLAND-1-catalog.md](ISLAND-1-catalog.md) | In progress | ISLAND-0 |
| 2 | Auth | [ISLAND-2-auth.md](ISLAND-2-auth.md) | In progress | ISLAND-0 |
| 3 | Test View | [ISLAND-3-test-view.md](ISLAND-3-test-view.md) | Pending | ISLAND-1 |
| 4 | Test Content | [ISLAND-4-test-content.md](ISLAND-4-test-content.md) | Pending | ISLAND-3 |
| 5 | Results | [ISLAND-5-results.md](ISLAND-5-results.md) | Pending | ISLAND-4 |
| 6 | History | [ISLAND-6-history.md](ISLAND-6-history.md) | Pending | ISLAND-5 |
| 7 | My Tests | [ISLAND-7-my-tests.md](ISLAND-7-my-tests.md) | Pending | ISLAND-1 |
| 8 | Profile | [ISLAND-8-profile.md](ISLAND-8-profile.md) | Pending | ISLAND-0 |

## How to use this manifest

1. Each island file starts with a **Goal** (what the subagent must build).
2. It then lists **Files to edit/create** with exact paths.
3. It references the **Design doc** in `docs/dev/frontend/` as the source of truth for visual layout.
4. It lists **API endpoints** from the generated SDK (`@/shared/api`).
5. It lists **Shared components** the island should use (already implemented or documented).
6. It gives **State management** guidance (Zustand vs localState vs TanStack Query).
7. It ends with **Testing / verification** instructions.

## Conventions every subagent must follow

### Tooling (non-negotiable)

- **Package manager:** `bun` (not pnpm, not npm)
- **Build check:** after finishing, run `npx vite build` — it must pass
- **API client:** `@hey-api/openapi-ts` generated client; do NOT write manual axios calls
- **Styling:** Tailwind CSS + shadcn/ui primitives (no raw CSS)
- **Forms:** `react-hook-form` + Zod (`zodResolver`) for all forms
- **State:** Zustand for client state; TanStack Query (`useQuery`/`useMutation`) for server state
- **Icons:** `lucide-react` only

### shadcn/ui component usage

All shadcn components are **named exports** in `@/shared/ui/<component>`:

```tsx
// ✅ CORRECT
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Card, CardContent } from '@/shared/ui/card'

// ❌ WRONG (default import)
import Button from '@/shared/ui/button'
import Input from '@/shared/ui/input'
```

### API client pattern

```tsx
import { someEndpoint } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'

// Query
const { data } = useQuery({
  queryKey: ['catalog', q, tags],
  queryFn: () => searchCatalogApiV1CatalogGet({ client, query: { q, tags: tags.join(','), skip: 0, limit: 20 } }),
})

// Mutation
const mutation = useMutation({
  mutationFn: (body: TestCreate) => createTestApiV1TestsPost({ client, body }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['my-tests'] })
  },
})
```

### Routing conventions

Always use `react-router-dom` `<Link to="...">` or `useNavigate()`.

| Page | Route |
|---|---|
| Catalog | `/catalog` |
| Login | `/login` |
| Register | `/register` |
| Test View | `/tests/:testId` |
| Take Test | `/tests/:testId/take` |
| Edit Test | `/tests/:testId/edit` |
| Settings | `/tests/:testId/settings` |
| History | `/history` |
| My Tests | `/my-tests` |
| Results | `/attempts/:attemptId` |
| Profile | `/profile` |

### Layout rule

**TopBar already exists** (`/widgets/top-bar/`). Do NOT create another header.
Every page should render its content below the 48px top bar.

```tsx
// In a page component, just wrap content:
export default function MyPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 pt-6 pb-12">
      {/* your content */}
    </div>
  )
}
```

### Design docs (source of truth)

All visual decisions are already documented in `docs/dev/frontend/`:

| Design doc | Coverage |
|---|---|
| `01-layout.md` | Top bar, navigation, content area rules |
| `02-catalog.md` | Grid cards, tags, search |
| `03-auth.md` | Login / Register forms |
| `04-test-view.md` | Test metadata + stats + CTA |
| `05-test-settings.md` | Metadata form (title, tags, visibility, time, attempt limit, completion screen) |
| `06-test-content-template.md` | Unified take/edit/review layout (the core UI) |
| `07-history.md` | Activity calendar + attempt list |
| `08-my-tests.md` | Author test cards + filtering |
| `09-results.md` | Review results (same template as take) |
| `10-profile.md` | Personal info + avatar |
| `11-backend-deps.md` | What backend must expose |
