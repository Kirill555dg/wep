# History — `/history`

Личная история прохождений тестов. Статистика, календарь активности, список попыток.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  History                                                     │
│                                                              │
│  ┌──────────── 1/2 ──────────┐ ┌────────── 1/2 ──────────┐│
│  │  Last Test Taken          │ │  Activity Calendar       ││
│  │  ──────────────────────── │ │ ─────────────────────── ││
│  │                           │ │                          ││
│  │  Linear Algebra Basics    │ │  April 2026              ││
│  │  Score: 12/15 (80%)      │ │                          ││
│  │  Time: 23m 14s           │ │  Mon Tue Wed Thu Fri Sat ││
│  │  Date: Today, 15:30      │ │  ──────────────────── ││
│  │                           │ │  [1] [2] [3] [4] [5] ││
│  │  [View Results]           │ │  [6] [7] [8] [9] ... ││
│  │                           │ │  ░░ ░░ ██ ░░ ░█ ░█ ░░││
│  └───────────────────────────┘ │                          ││
│                                 └──────────────────────────┘│
│                                                              │
│  All attempts:                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Linear Algebra Basics   80%  15.03.2026  23m  [View] │   │
│  │ Python Fundamentals     91%  10.03.2026  19m  [View] │   │
│  │ Database 101            75%  05.03.2026  30m  [View] │   │
│  │ Calculus Midterm        65%  28.02.2026  45m  [View] │   │
│  │ ...more...                                            │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  [Load More]                                                 │
└──────────────────────────────────────────────────────────────┘
```

## Last Test Taken

| Элемент | Данные |
|---|---|
| Test name | `attempt.test_title` — `text-xl font-semibold` |
| Score | `attempt.score / attempt.max_score` |
| Percent | `round(score/max_score * 100)%` |
| Time | `formatTime(attempt.time_spent)` |
| Date | Relative ("Today, 15:30", "Yesterday", "15 Mar 2026") |
| View button | → `/attempts/:id` |

### States

| State | Показывать |
|---|---|
| Has attempts | Last test card with data |
| No attempts | Empty state: "You haven't taken any tests yet" |

## Activity Calendar

GitHub-style contribution calendar.

### Layout

```
  April 2026
┌─────────────────────────────────────────────────────┐
│  Mon │  ░░  ░░  ░░  ░░  ░░  ░░                     │
│  Tue │  ░░  ░░  ░░  ░░  ██  ░█                     │
│  Wed │  ░░  ░░  ██  ██  ██  ░░                     │
│  Thu │  ░░  ██  ░█  ░█  ░░  ░░                     │
│  Fri │  ░░  ░░  ░░  ░░  ░░  ░░                     │
│  Sat │  ░░  ░░  ░░  ░░  ░░  ░░                     │
│  Sun │  ░░  ░░  ░░  ░░  ░░  ░░                     │
└─────────────────────────────────────────────────────┘
  Less                    More
```

| Color | Attempts |
|---|---|
| `░░` (bg-muted) | 0 |
| `░█` (green-200) | 1 |
| `█░` (green-400) | 2-3 |
| `██` (green-600) | 4+ |

### Navigation

- Month switcher: `< April 2026 >`
- Data: `GET /stats/calendar?year=2026&month=4`

### Interaction

- Hover over cell → tooltip: "3 tests taken on Apr 15"
- Click on cell → filter attempts list below to that day

## Attempts List

Columns:

| Column | Data | Format |
|---|---|---|
| Test | `attempt.test_title` | Link to Test View `/tests/:id` |
| Score | `score/max_score (percent%)` | Score + percent |
| Date | `attempt.created_at` | Formatted date |
| Time | `attempt.time_spent` | "23m" |
| Action | [View] button | → `/attempts/:id` |

### Sorting

Default: newest first.
Options: score (high-low), date (new-old), time (fast-slow).

### Pagination

- Default: 20 per page
- [Load More] at bottom

## Actions

| Действие | Триггер | Результат |
|---|---|---|
| View attempt | Click [View] or row | → `/attempts/:id` |
| View test | Click test name | → `/tests/:id` |
| Filter by date | Click calendar cell | Filter list |
| Change month | Calendar nav | Reload calendar data |
| Load more | [Load More] | Append next page |

## Empty state

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              📋                                               │
│     No test history yet                                      │
│     Browse the catalog to find your first test               │
│                                                              │
│              [Browse Catalog]                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```
