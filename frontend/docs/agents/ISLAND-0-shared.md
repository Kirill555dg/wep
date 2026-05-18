# ISLAND-0: Shared Infrastructure (DONE)

This island is **NOT a task for a subagent** — it documents what already exists.
Subagents building other islands should reference this to avoid reimplementing existingcomponents.

## What's already implemented

### API client

| File | Exports |
|---|---|
| `@/shared/api/index.ts` | All generated SDK functions + types re-exported |
| `@/shared/api/generated/sdk.gen.ts` | Auto-generated `searchCatalogApiV1CatalogGet`, `loginApiV1AuthLoginPost`, etc. |
| `@/shared/api/generated/types.gen.ts` | Auto-generated `TestResponse`, `LoginRequest`, etc. |
| `@/shared/api/generated/client.gen.ts` | `client` — pass as `{ client }` option to every SDK call |

**Remember:** every SDK call needs `client`:
```ts
import { client } from '@/shared/api/generated/client.gen'
const res = await searchCatalogApiV1CatalogGet({ client })
```

### Auth & auth state

| File | What it does |
|---|---|
| `@/entities/user/model/store.ts` | `useUserStore` — Zustand store with `user`, `token`, `setUser`, `setToken`, `logout` |
| `@/shared/hooks/useAuth.ts` | `useAuth()` — returns `{ user, token, isAuthed, logout, requireAuth }` |
| `@/shared/hooks/useApi.ts` | `useApiQuery()`, `useApiMutation()`, `useInvalidate()` — TanStack Query wrappers |

`useAuth().requireAuth(path)` redirects unauthenticated users to `/login?redirect=path`.

### Navigation

| File | What it does |
|---|---|
| `@/widgets/top-bar/TopBar.tsx` | Sticky 48px bar with logo (→/catalog), nav links (My Tests, History), user dropdown (Profile, Sign out) |

### Routing

| File | Done? |
|---|---|
| `@/app/router.tsx` | All routes registered as of latest commit |
| `@/main.tsx` | Providers + TopBar + AppRouter |

### Placeholder pages (stubs every subagent will replace)

| Page | Route | File |
|---|---|---|
| CatalogPage | `/catalog` | `src/pages/catalog/CatalogPage.tsx` |
| LoginPage | `/login` | `src/pages/login/LoginPage.tsx` |
| RegisterPage | `/register` | `src/pages/register/RegisterPage.tsx` |
| ProfilePage | `/profile` | `src/pages/profile/ProfilePage.tsx` |
| TestViewPage | `/tests/:testId` | `src/pages/test-view/TestViewPage.tsx` |
| TakeTestPage | `/tests/:testId/take` | `src/pages/test-content/TakeTestPage.tsx` |
| HistoryPage | `/history` | `src/pages/history/HistoryPage.tsx` |
| MyTestsPage | `/my-tests` | `src/pages/my-tests/MyTestsPage.tsx` |
| ResultsPage | `/attempts/:attemptId` | `src/pages/results/ResultsPage.tsx` |
| TestSettingsPage | `/tests/:testId/settings` | `src/pages/test-settings/TestSettingsPage.tsx` |

**Subagents must replace the placeholder** for their assigned page, not create a new file.

### shadcn/ui components available

All in `src/shared/ui/`. Every component is a **named export** (never default):

- `Button`, `Input`, `Textarea`, `Select`, `Switch`, `Checkbox`
- `Card`, `CardHeader`, `CardContent`, `CardTitle`, `CardDescription`
- `Dialog`, `DropdownMenu`, `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`
- `Toast`, `Avatar`, `AvatarImage`, `AvatarFallback`, `Badge`, `Label`

### lucide-react icons available

Use directly:
- `Infinity`, `Plus`, `Trash2`, `Pencil`, `Check`, `X`, `ChevronLeft`, `ChevronRight`
- `Search`, `Upload`, `Download`, `Clock`, `Timer`, `Play`, `Pause`
- `Eye`, `EyeOff`, `Settings`, `User`, `LogOut`, `Menu`, `GripVertical`

### Attempt cache

| File | What it does |
|---|---|
| `@/shared/hooks/useAttemptCache.ts` | `useAttemptCache(testId)` — loads/saves answers to localStorage during test taking |

**Key format:** `wep_attempt_${testId}`

### Typst rendering

| File | Status |
|---|---|
| `@/features/render/ui/TypstPreview.tsx` | ✅ Exists, renders Typst source to SVG |

The `typst.ts` WASM library is already set up (vite-plugin-wasm). If a subagent needs to render Typst content, they can use the existing component or call the library directly.

### Subagent checklist

Before starting work on any page, a subagent must verify the shared infrastructure:

1. ✅ `bun` works (run `bun --version`)
2. ✅ `npx vite build` passes from a clean checkout
3. ✅ The desired API endpoint exists in `@/shared/api`
4. ✅ The desired shadcn/ui component exists in `@/shared/ui`

If any of these fail, the subagent must report back instead of implementing a workaround.
