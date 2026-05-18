# WEP Frontend — Design Overview

## Purpose

Документ описывает дизайн фронтенда платформы WEP (Web Education Platform) — интерактивного конструктора образовательных тестов.

## Pages

| # | Страница | Роут | Auth | Дизайн-док |
|---|---|---|---|---|
| 1 | Login | `/login` | Нет | [03-auth.md](./03-auth.md) |
| 2 | Register | `/register` | Нет | [03-auth.md](./03-auth.md) |
| 3 | Catalog (главная) | `/catalog` | Нет* | [02-catalog.md](./02-catalog.md) |
| 4 | Test View | `/tests/:testId` | Нет* | [04-test-view.md](./04-test-view.md) |
| 5 | Test Settings | `/tests/:testId/settings` | Да | [05-test-settings.md](./05-test-settings.md) |
| 6 | Test Content | `/tests/:testId/take` | Да | [06-test-content-template.md](./06-test-content-template.md) |
| 6 | Test Content (edit) | `/tests/:testId/edit` | Да | [06-test-content-template.md](./06-test-content-template.md) |
| 7 | History | `/history` | Да | [07-history.md](./07-history.md) |
| 8 | My Tests | `/my-tests` | Да | [08-my-tests.md](./08-my-tests.md) |
| 9 | Results | `/attempts/:attemptId` | Да | [09-results.md](./09-results.md) |
| 10 | Profile | `/profile` | Да | [10-profile.md](./10-profile.md) |

*\* — страница видна без авторизации, но действие требует логина*

## Shared components

- `TopBar` (header) — [01-layout.md](./01-layout.md)
- `TestCard` — catalog card, reused on `/catalog` and `/my-tests`
- `QuestionPanel` — side panel with question list
- `QuestionArea` — typst render + media + answers (the unified template)
- `TypstRender` — typst renderer (no zoom UI, native scaling only)
- `MediaCarousel` — 0-10 media files with type-aware display
- `QuestionEditorModal` — typst source editor + live render
- `Calendar` — GitHub-style activity calendar
- `StatCard` — metric card with value + label + optional trend
- `ScoreBar` — horizontal progress bar for per-question stats

## Design principles

1. **Единый шаблон содержимого**: take / edit / review используют один и тот же layout вопросов. Отличаются только controls (answer vs edit vs read-only).
2. **Минимальный интерфейс**: никакого постоянного хедера/футера. Только тонкая top bar с навигацией.
3. **Catalog — главная страница**: пользователь сразу видит тесты, без лишних дашбордов.
4. **Консистентность**: карточки тестов выглядят одинаково везде (catalog, my-tests).
5. **Typst-first**: весь контент рендерится Typst, с зумом и фулскрином.

## Tech stack

| Технология | Назначение |
|---|---|
| React 18 + TypeScript | UI framework |
| Vite | Bundler |
| Tailwind CSS + shadcn/ui | Styling |
| @tanstack/react-query | Server state |
| Zustand | Client state |
| @hey-api/openapi-ts | API client (from OpenAPI spec) |
| @myriaddreamin/typst.ts | Math/formatted text rendering |
| react-router-dom v6 | Routing |
| react-hook-form + zod | Form validation |
| lucide-react | Icons |

## UI components strategy

Use only what is already in the project (`shared/ui/` shadcn/ui and `lucide-react`). No new UI dependencies.

**shadcn/ui components** (already in `src/shared/ui/`):
- `Button` | `Input` | `Textarea` | `Select` | `Switch`
- `RadioGroup` | `Checkbox` | `Card` | `Badge` | `Dialog`
- `DropdownMenu` | `Tabs` | `Toast` | `Avatar` | `Loader`

**lucide-react icons we use**:
- `Infinity` — Unlimited toggle (max attempts)
- `X` / `Plus` / `Trash2` / `Pencil` / `Check` / `GripVertical` (drag)
- `ChevronLeft` / `ChevronRight` | `Clock` | `Play` | `Upload`

If something is not in `shared/ui/`, compose it from shadcn primitives + tailwind. No new library.

## Cleanup

При реализации удалить:

- `widgets/auth/`, `widgets/dashboard/`, `widgets/test-editor/`
- `shared/api/client.ts`, `shared/api/manual.tsx`, `shared/api/simpleApi.tsx`
- `orval.config.js`, `shared/api/client/` (orval generated)
- `pages/stats/` (merged into test-view/history)
- `pages/results/` → переписать под новый дизайн
- Все старые страницы, несовместимые с новым роутингом

## File structure

```
src/
├── app/
│   ├── router.tsx           # All routes
│   ├── providers.tsx        # QueryClient, etc.
│   └── guards/
│       └── AuthGuard.tsx
├── pages/
│   ├── catalog/             # /catalog
│   ├── auth/                # /login, /register
│   ├── test-view/           # /tests/:id
│   ├── test-settings/       # /tests/:id/settings
│   ├── test-content/        # /tests/:id/take, /tests/:id/edit
│   ├── history/             # /history
│   ├── my-tests/            # /my-tests
│   ├── results/             # /attempts/:id
│   └── profile/             # /profile
├── widgets/                 # Reusable composite blocks
│   ├── top-bar/
│   ├── test-card/
│   ├── question-panel/
│   ├── question-area/
│   ├── media-carousel/
│   ├── calendar/
│   ├── question-editor-typst/   # Typst live-render sub-page
├── features/                # User scenarios
│   ├── auth/
│   ├── taking/
│   ├── test-management/
│   └── stats/
├── entities/                # Domain models + stores
│   ├── user/
│   └── attempt/
└── shared/                  # Infrastructure
    ├── api/                  # @hey-api generated client
    ├── ui/                   # shadcn/ui components
    ├── lib/                  # utils, typst renderer
    ├── hooks/                # useToast, etc.
    └── styles/               # globals.css
```
