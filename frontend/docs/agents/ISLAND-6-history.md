# ISLAND-6: History Page (`/history`)

## Goal

Build the **history page** — shows personal test history with:
- Most recent test taken (card)
- Activity calendar (GitHub-style heatmap)
- Paginated list of past attempts

## Design reference

`docs/dev/frontend/07-history.md`

## Files to modify

| File | Action |
|---|---|
| `src/pages/history/HistoryPage.tsx` | Replace placeholder |

## Component architecture

```
HistoryPage
├── useAuth check (redirect to login if not authed)
├── RecentTestCard
│   ├── Test title + score
│   ├── Time spent
│   ├── Date
│   └── [View Results] → /attempts/:id
├── ActivityCalendar
│   ├── Month switcher
│   └── Day grid (Mo-Su)
│       └── Color intensity based on attempts taken that day
└── AttemptList
    ├── Filter tabs: [All | Completed | Expired]
    └── Rows
        ├── Test title (link → /tests/:id)
        ├── Score / max
        ├── Percent
        ├── Date
        └── [View] → /attempts/:id
```

### Data

```tsx
// Recent attempt
const { data: attempts } = useQuery({
  queryKey: ['my-attempts'],
  queryFn: () => /* needs backend endpoint: GET /attempts (user's own) */
})

// Author stats for calendar
const { data: stats } = useQuery({
  queryKey: ['my-stats'],
  queryFn: () => getAuthorStatsApiV1StatsMeGet({ client }),
})
```

**Note:** Calendar data endpoint (`GET /stats/calendar`) is a backend dependency (see `docs/dev/frontend/11-backend-deps.md`). Until implemented, the calendar can be a placeholder or hardcoded mock.

### ActivityCalendar

Use a simple grid layout (CSS grid, 7 columns for days, 4-5 rows for weeks).

Color scale (Tailwind classes):
- 0 attempts: `bg-gray-100`
- 1 attempt: `bg-green-200`
- 2-3: `bg-green-400`
- 4+: `bg-green-600`

Month navigation: `<` `>` arrows.

On hover: tooltip with day and count of attempts.

On click: filter AttemptList to that day.

### AttemptList rows

```
Linear Algebra Basics    80%    15.03.2026    23m    [View]
```

Sort by: date descending (default). Optional: score, date.

**Note:** the backend doesn't yet have a `GET /attempts` list endpoint for the current user. A new endpoint was listed in backend deps. Until available, this can be a placeholder or mock.

## Verification checklist

- [ ] Build passes
- [ ] Requires auth (redirect if not)
- [ ] Shows recent attempt card at top
- [ ] Calendar grid renders
- [ ] Attempt list shows (or placeholder)
- [ ] Rows link to test and attempt result

## Design file

`docs/dev/frontend/07-history.md`

## Related islands

- **ISLAND-5 (Results)** — [View] links here
- **ISLAND-8 (Profile)** — back link
- **ISLAND-3 (Test View)** — test title link
