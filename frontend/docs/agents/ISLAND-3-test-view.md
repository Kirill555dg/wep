# ISLAND-3: Test View Page (`/tests/:testId`)

## Goal

Build the **test view page** — the "about this test" page every user sees.
It shows metadata, statistics, and the CTA to start/continue/retake the test.

## Design reference

`docs/dev/frontend/04-test-view.md`

Key visual points:
- Cover image or gradient fallback
- Title + tags + author meta
- Description (Typst-rendered if formulas present)
- CTA button: `[Start Test]` / `[Continue Test]` / `[Retake Test]`
- If author: `[Edit]` link to settings, public stats cards

## Files to modify

| File | Action |
|---|---|
| `src/pages/test-view/TestViewPage.tsx` | Replace placeholder |

## Component architecture

```
TestViewPage
├── CoverImage            (320×200, gradient fallback)
├── MetaHeader            (title + tags + author)
│   └── TagChips          (click → /catalog?tag=slug)
├── DescriptionBlock      (Typst-rendered or plain text)
├── MetaBar               (questions · time · visibility)
├── CTA                   (depends on user state)
└── StatsSection          (author only)
    ├── StatCards         (takes · avg · time)
    ├── ScoreDistribution  (bar chart, SVG or recharts)
    └── QuestionStatsList  (correctness per question)
```

### Data fetching

```tsx
const { testId } = useParams()
const { isAuthed, user } = useAuth()

// Public metadata
const { data: test } = useQuery({
  queryKey: ['test', testId],
  queryFn: () => getPublicTestApiV1CatalogTestIdGet({ client, path: { test_id: Number(testId) } }),
})

// Author detail (if authed and is author)
const { data: authorDetail } = useQuery({
  queryKey: ['test-author', testId],
  queryFn: () => getTestApiV1TestsTestIdGet({ client, path: { test_id: Number(testId) } }),
  enabled: isAuthed && test?.author_id === user?.id,
})
```

**Public vs author detail:**
- Public: `getPublicTestApiV1CatalogTestIdGet` returns `TestDetailResponse` (no answers, no attempt limit)
- Author: `getTestApiV1TestsTestIdGet` returns `TestAuthorDetailResponse` — includes `attempt_limit`, `completion_message`, and author-only question details

### CTA button logic

| User state | Button label | Link |
|---|---|---|
| Not authed | `Войти чтобы пройти` | `/login?redirect=/tests/${id}` |
| Authed, never took | `Начать тест` | POST `/attempts` → `/tests/${id}/take` |
| Authed, attempt in progress | `Продолжить тест` | `/tests/${id}/take` (resume) |
| Authed, finished, limit allows | `Пройти снова` | POST `/attempts` → `/tests/${id}/take` |
| Authed, limit exhausted | `Лимит попыток исчерпан` | disabled |

### Stats (author only)

```tsx
const { data: stats } = useQuery({
  queryKey: ['test-stats', testId],
  queryFn: () => getTestStatsApiV1StatsTestsTestIdGet({
    client,
    path: { test_id: Number(testId) }
  }),
  enabled: isAuthor,
})
```

Show:
- `total_attempts` — total takes
- `completed_attempts` — finished takes
- `avg_score` / `avg_score_percent` — average percent
- `avg_time` — average minutes
- Score distribution bar chart (see design doc)
- Per-question accuracy list (Q1: 92%, Q2: 78%, ...)

### Cover image

If `test` has an associated media file, display it. Otherwise:
```tsx
defaultClassName="bg-gradient-to-br from-indigo-100 to-blue-50 h-64 rounded-xl flex items-center justify-center"
```

### Author controls

If current user is the test author:
- `[Редактировать]` → `/tests/${id}/edit`
- `[Настройки]` → `/tests/${id}/settings`

## Verification checklist

- [ ] Build passes
- [ ] Page fetches test public metadata correctly
- [ ] Author view shows extra fields (`attempt_limit`, `completion_message`, stats)
- [ ] CTA buttons differ by user attempt state
- [ ] Stats section only visible to author
- [ ] Tag chips link to catalog filtered by tag
- [ ] Author name links to catalog filtered by author
- [ ] Description is Typst-rendered if it contains formulas
- [ ] Limit exhaustion disables Retake button with tooltip

## Backend dependencies (done)

- `GET /api/v1/catalog/:id` — `getPublicTestApiV1CatalogTestIdGet`
- `GET /api/v1/tests/:id` — `getTestApiV1TestsTestIdGet`
- `GET /api/v1/stats/tests/:id` — `getTestStatsApiV1StatsTestsTestIdGet`
- `POST /api/v1/attempts` — `startAttemptApiV1AttemptsPost`

## Related islands

- **ISLAND-1 (Catalog)** — for tag/author filter links
- **ISLAND-4 (Test Content)** — for taking / editing the test
- **ISLAND-7 (My Tests)** — for `Редактировать` if author

## Design file

`docs/dev/frontend/04-test-view.md`
