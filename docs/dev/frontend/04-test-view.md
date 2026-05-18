# Test View — `/tests/:testId`

Страница просмотра теста. Показывает метаинформацию, описание, автора, теги. Если пользователь — автор теста, дополнительно показывает **обезличенную статистику** и кнопки управления.

Это НЕ страница прохождения. Это страница "о тесте".

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  ← Back to Catalog                                           │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  🖼  Cover image (optional, h-64 w-full rounded)   │     │
│  │     или градиент-заглушка из названия              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  Linear Algebra Basics                                       │
│  [Mathematics] [Algebra]                                      │
│                                                              │
│  by John Doe  •  Created 15.03.2026                         │
│                                                              │
│  15 questions  •  30 min  •  Attempts: 0/3  •  ⏱ Tracked  •  🔒 Private / 🌍 Public  │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Description:                                      │     │
│  │  A comprehensive test covering matrices,           │     │
│  │  determinants, and vector spaces. Designed for     │     │
│  │  first-year students.                              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  [Start Test] / [Continue Test] / [Retake Test] │     │
│  │  or (if author) [Edit Questions →]  [Settings]    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ———— (если автор) ————                                   │
│                                                              │
│  Statistics                                                 │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌────────────────────────┐    │
│  │  120 │ │ 82%  │ │15min │ │  Score distribution     │    │
│  │ takes│ │ avg  │ │ avg  │ │  [LeetCode-style chart] │    │
│  └──────┘ └──────┘ └──────┘ └────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Questions by correctness:                        │     │
│  │                                                   │     │
│  │  Q1: "What is determinant?"    92%  █████████░░  │     │
│  │  Q2: "Solve matrix equation"   78%  ████████░░░  │     │
│  │  Q3: "Vector space axioms"     85%  █████████░░  │     │
│  │  ...                                               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ———— (если автор) ————                                   │
│                                                              │
│  Recent attempts (anonymous):                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │ User A     12/15   82%   15.03.2026  23m           │     │
│  │ User B     10/15   66%   14.03.2026  19m           │     │
│  │ User C     15/15  100%   14.03.2026  30m           │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Elements

### Cover image

- `h-64 w-full object-cover rounded-xl`
- Если у теста есть медиа-файл, помеченный как обложка — показать его
- Иначе градиент на основе названия теста (детерминированный цвет)

### Meta bar

| Элемент | Данные |
|---|---|
| Title | `test.title` — `text-3xl font-bold` |
| Tags | `test.tags` — chips, клик → `/catalog?tag=slug` |
| Author | `test.author` — click → `/catalog?authorId=id` |
| Created | `test.created_at` formatted |
| Questions | `test.questions_count` |
| Duration | `test.time_limit_minutes` |
| Attempts | Hidden if `attempt_limit is None`; otherwise `attempts_used / attempt_limit` |
| Time tracking | `⏱ Tracked` / `⏱ Not tracked` indicator |
| Visibility | Public/Private badge |

### CTA button

| Состояние | Кнопка | Действие |
|---|---|---|
| Не авторизован | `[Login to Start]` | → `/login?redirect=/tests/:id` |
| Никогда не проходил | `[Start Test]` | POST `/attempts` → `/tests/:id/take` |
| Есть активная попытка | `[Continue Test]` | → `/tests/:id/take` (возобновление) |
| Завершен, лимит позволяет | `[Retake Test]` | POST `/attempts` → `/tests/:id/take` |
| Завершен, лимит исчерпан | — | Показать "Attempt limit reached" |
| Автор | `[Edit Questions →]` | → `/tests/:id/edit` |

> **Limit check:** Retake shown only if `attempt_limit is None` (unlimited) or `attempts_used < attempt_limit`.

### Description

- Prose block, рендерится как Markdown или Typst (если содержит формулы)
- `text-base leading-relaxed text-gray-700`

## Author-only sections

> **Public tests (non-author):** stats shown here are **per last attempt** of the current user (not aggregate).

### Stats cards

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│  120     │  │  82%     │  │  15min   │
│  takes   │  │ avg score│  │ avg time │
│  (+12%📈)│  │  (-3%📉) │  │          │
└──────────┘  └──────────┘  └──────────┘
```

- 3 stat cards in a row
- Change indicator optional (percent vs last week/month)

### Score distribution chart

Bar chart (simple SVG or recharts/lib):
```
100% ┤ ████
 80% ┤ ████████
 60% ┤ ████████████
 40% ┤ ██████
 20% ┤ ███
  0% ┤───┬───┬───┬───┬───┬───
```

### Questions by correctness

Horizontal progress bar per question:

```
Q1: "What is determinant?"     92%  ████████████████████░░░░
Q2: "Solve matrix equation"    78%  ██████████████████░░░░░░
```

- Сортировка по номеру вопроса
- Клик по вопросу → модалка с деталями (как в results)

### Recent attempts

- Анонимные (User A, User B, ...)
- Columns: user, score, percent, date, time
- Paginated (10 per page)

## Actions

| Действие | Автор? | Триггер | Результат |
|---|---|---|---|
| Go back | All | Click "← Back" | Navigate back |
| Read author | All | Click author | `/catalog?authorId=X` |
| Filter by tag | All | Click tag | `/catalog?tag=slug` |
| Start / Continue / Retake | Not author, authed | Click CTA | POST/GET `/attempts` → `/tests/:id/take` |
| Edit questions | Author | Click "Edit" | → `/tests/:id/edit` |
| Open settings | Author | Click "Settings" | → `/tests/:id/settings` |
| View attempt stats | Author | Click attempt row | → `/attempts/:attemptId` |

## States

| State | Что видно |
|---|---|
| Loading | Skeleton: cover + title + description + stats |
| Not found | "Test not found" + back link |
| Private (non-author) | "This test is private" message |
| Error | "Failed to load test" + retry btn |
