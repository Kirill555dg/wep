# My Tests — `/my-tests`

Список тестов, созданных текущим пользователем. Использует ту же сетку, поиск и фильтры, что и страница каталога.

По умолчанию применяется фильтр `author = current user`. Доступны те же tag-chips для фильтрации, что и в каталоге. В правом верхнем углу страницы размещена кнопка `[+ New Test]`.

> **Layout:** та же карточная сетка, что и в каталоге, с дополнительными элементами управления.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  My Tests                                   [+ New Test]    │
│                                                              │
│  [All] [Published] [Private]                                 │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  🖼         │ │  🖼         │ │  🖼         │          │
│  │  320×200    │ │  320×200    │ │  320×200    │          │
│  │             │ │             │ │             │          │
│  │ Linear      │ │ Draft       │ │ Calculus    │          │
│  │ Algebra     │ │ Quiz        │ │ Midterm     │          │
│  │             │ │             │ │             │          │
│  │ 🟢 Published│ │ 🔒 Private  │ │ 🟢 Published│          │
│  │ 120 takes   │ │ 0 takes     │ │ 45 takes    │          │
│  │ 82% avg     │ │ —           │ │ 70% avg     │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                              │
│  [Load More]                                                 │
└──────────────────────────────────────────────────────────────┘
```

## Filter tabs

| Tab | Filter |
|---|---|
| All | Все тесты |
| Published | `is_public == true` |
| Private | `is_public == false` |

## Test card (My Tests variant)

Same as catalog card layout (320x200 image, title, tags), but bottom section shows different data:

```
                  ┌──────────────────────────────┐
                  │                              │
                  │  🟢 Published   120 takes    │
                  │  82% avg score  Created date │
                  │                              │
                  │        [Edit] [Stats]        │
                  └──────────────────────────────┘
```

### Bottom section

| State | Badge | Data shown |
|---|---|---|
| Public | `🟢 Published` | takes count, avg score |
| Private | `🔒 Private` | takes count (usually 0) |

### Card actions

| Действие | Триггер | Результат |
|---|---|---|
| Edit questions | Click [Edit] or card | → `/tests/:id/edit` |
| View test | Click test name | → `/tests/:id` |
| View stats | Click [Stats] | → `/tests/:id` (scroll to stats) |
| Delete | Long press or context menu | Confirm dialog → DELETE |

## [+ New Test]

| Аспект | Детали |
|---|---|
| Position | Top right of page |
| Type | Button `bg-primary text-primary-foreground` |
| Action | POST `/tests/` with defaults → redirect `/tests/:id/edit` |

Default new test:
```json
{
  "title": "Untitled Test",
  "description": "",
  "is_public": false,
  "time_limit_minutes": null,
  "tag_names": []
}
```

## Empty state

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              📝                                               │
│     You haven't created any tests yet                        │
│                                                              │
│              [Create Your First Test]                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Actions

| Действие | Триггер | Результат |
|---|---|---|
| New test | Click [+ New Test] | POST → redirect to `/tests/:id/edit` |
| Edit test | Click [Edit] | → `/tests/:id/edit` |
| View test | Click card | → `/tests/:id` |
| Filter | Click tab | Filter list by visibility |
| Load more | Click [Load More] | Paginate |
