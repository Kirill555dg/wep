# Catalog — `/catalog`

Главная страница приложения. Публичный каталог тестов. Без авторизации — просмотр, с авторизацией — прохождение.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  Search: ┌────────────────────────────────────┐ [Search]   │
│          │ Поиск тестов...                     │            │
│          └────────────────────────────────────┘            │
│                                                              │
│  Tags: [Все] [Mathematics] [Physics] [CS] [Biology]        │
│                                                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │  🖼         │ │  🖼         │ │  🖼         │          │
│  │  320×200    │ │  320×200    │ │  320×200    │          │
│  │             │ │             │ │             │          │
│  │ Linear      │ │ Python      │ │ Database    │          │
│  │ Algebra     │ │ Fund.       │ │ 101         │          │
│  │             │ │             │ │             │          │
│  │ [Math]      │ │ [CS]        │ │ [DB]        │          │
│  │ John Doe    │ │ Jane Smith  │ │ Bob Brown   │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   ...       │ │   ...       │ │   ...       │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                              │
│  [Load More]                                                 │
└──────────────────────────────────────────────────────────────┘
```

## Search bar

- `h-10` search input
- Placeholder: "Поиск тестов..."
- Debounced (300ms)
- При вводе — фильтрация по названию
- Кнопка поиска (лупа)

## Tags filter

Horizontally scrollable row of tag chips:

```
[Все] [Mathematics] [Physics] [CS] [Biology] [History] [Languages]
```

- `[Все]` — сброс фильтра, показывать всё
- Клик по тегу — `active` state (filled), остальные — outline
- Multiple tags selectable (OR-фильтрация: тест показывается, если содержит любой из выбранных)
- Если тегов много — horizontal scroll (`overflow-x-auto hide-scrollbar`)

## Test card

Размер карточки: `w-[320px]` (или `calc(100%/3 - gap)` в гриде).

```
320px
┌──────────────────────────────┐
│  ┌────────────────────────┐  │ 200px
│  │  Image (test thumbnail) │  │
│  │  or gradient fallback   │  │
│  └────────────────────────┘  │
│                              │
│  Linear Algebra Basics       │
│  [Mathematics] [Algebra]     │
│                              │
│  John Doe                    │
│  15 qns  •  30 min          │
│                              │
└──────────────────────────────┘
```

### Card states

| State | Визуал | Поведение клика |
|---|---|---|
| Default | Full card | → `/tests/:testId` (Test View) |
| Hover | Subtle shadow + translateY(-2px) | — |
| Loading | Skeleton shimmer | — |
| Empty (no image) | Gradient placeholder (из `title`) | — |

### Card actions

| Действие | Как |
|---|---|
| Open test | Click card |
| Open author | Click author name → `/catalog?authorId=X` |

### Card элементы

| Элемент | Поведение |
|---|---|
| Изображение | Первое медиа из теста или fallback-градиент |
| Название | `font-semibold text-base truncate` |
| Теги | Chips, клик → filter by tag |
| Автор | `text-sm text-muted-foreground`, клик → filter by author |
| Мета | `text-xs text-muted-foreground`: questions count, time |

> **Note:** Tag chips on test cards are clickable and filter catalog by that tag.
> **Note:** Author name is clickable and filters by author.

## Empty state

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Когда нет тестов по фильтру:                                │
│                                                              │
│              🔍                                               │
│     No tests found                                           │
│     Try adjusting your search or filters                     │
│                                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Error state

```
┌──────────────────────────────────────────────────────────────┐
│              ⚠️                                              │
│     Failed to load tests                                     │
│     [Retry]                                                  │
└──────────────────────────────────────────────────────────────┘
```

## Pagination / Load more

Кнопка `[Load More]` внизу, если `total > items.length`.
Use cursor-based or offset pagination (backend: skip/limit).

## Grid layout

- Responsive grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`
- Gap: `gap-6`
- Padding content: `pt-6 pb-12`
