# Test Settings — `/tests/:testId/settings`

Страница редактирования метаинформации теста. Только для автора теста.

НЕ включает редактирование вопросов — для этого есть `/tests/:id/edit`.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  ← Back to Test                                              │
│                                                              │
│  Test Settings                                               │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Title                                              │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │ Linear Algebra Basics                        │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │                                                    │     │
│  │  Description (Typst-supported)                     │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │ A comprehensive test covering $n xx n$       │  │     │
│  │  │ matrices, determinants, and vector            │  │     │
│  │  │ spaces.                                       │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │                                                    │     │
│  │  Visibility                                        │     │
│  │  [● Public]  [○ Private]                           │     │
│  │                                                    │     │
  │  │  Time limit                                        │     │
  │  │  ┌──────────────────┐                              │     │
  │  │  │ 30              │ min  (empty = no limit)     │     │
  │  │  └──────────────────┘                              │     │
  │  │                                                    │     │
  │  │  Track completion time                             │     │
  │  │  [● Yes]  [○ No]                                   │     │
  │  │                                                    │     │
  │  │  Max attempts per user                              │     │
  │  │  ┌───────┐ ┌──────────┐                            │     │
  │  │  │  3    │ │  ∞ ☁️   │  ← num input + icon btn   │     │
  │  │  └───────┘ └──────────┘  (tooltip "Unlimited")   │     │
  │  │                                                    │     │
  │  │  Tags                                              │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │ [Mathematics ✕] [Algebra ✕]                  │  │     │
│  │  │ [Type to search or create...                ]│  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │                                                    │     │
│  │  Cover image                                       │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  [Current cover preview]   [Change] [Remove] │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  │                                                    │     │
  │  │  Completion screen                                 │     │
  │  │  ┌──────────────────────────────────────────────┐  │     │
  │  │  │  Enable custom completion screen              │  │     │
  │  │  │  [● Enable] [○ Disable]                      │  │     │
  │  │  │                                               │  │     │
  │  │  │  Message 100-80% (Typst):                   │  │     │
  │  │  │  ┌────────────────────────────────────────┐  │  │     │
  │  │  │  │ Excellent! You scored #score/#max.      │  │     │
  │  │  │  └────────────────────────────────────────┘  │  │     │
  │  │  │  [🏞 trophy.png] [+ Add]                   │  │     │
  │  │  │                                               │  │     │
  │  │  │  Message 79-50% (Typst):                    │  │     │
  │  │  │  ┌────────────────────────────────────────┐  │  │     │
  │  │  │  │ Good effort! You scored #score/#max.    │  │     │
  │  │  │  └────────────────────────────────────────┘  │  │     │
  │  │  │  [+ Add media]                             │  │     │
  │  │  │                                               │  │     │
  │  │  │  Message <50% (Typst):                     │  │     │
  │  │  │  ┌────────────────────────────────────────┐  │  │     │
  │  │  │  │ Keep trying! You scored #score/#max.    │  │     │
  │  │  │  └────────────────────────────────────────┘  │  │     │
  │  │  │  [+ Add media]                             │  │     │
  │  │  └──────────────────────────────────────────────┘  │     │
│  │                                                    │     │
│  │  [Save Changes]  [Cancel]                         │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Form fields

### Title
| Аспект | Детали |
|---|---|
| Type | `input type="text"` |
| Validation | Required, 1-255 chars |

### Description
| Аспект | Детали |
|---|---|
| Type | `textarea` rows=4 |
| Validation | Optional |
| Render | Typst-supported, preview toggle? |

### Visibility
| Аспект | Детали |
|---|---|
| Type | Radio group |
| Options | Public / Private |

### Time limit
| Аспект | Детали |
|---|---|
| Type | `input type="number" min=1` + select "minutes" |
| Validation | Optional, >= 1 |

> **Note:** Visibility changes affect attempt defaults automatically (public = unlimited/null, private = 1 attempt) but can be overridden manually.

### Max attempts per user

| Аспект | Детали |
|---|---|
| Type | `input type="number" min=0` |
| Label | Max attempts per user |
| Default | "Unlimited" (backend: `null`) for public, 1 for private |
| Display | Number input + `Infinity` icon button (tooltip: "Unlimited") |
| Validation | If limited: integer >= 1 |

```
┌─── Max attempts per user ───┐
│ ┌───────┐ ┌──────────┐    │
│ │  3    │ │  ∞ ☁️   │    │ ← number input + icon button
│ └───────┘ └──────────┘    │   (icon tooltip: "Unlimited")
└─────────────────────────────┘
```

- **Number input**: simple integer input (`min=0`)
- **Infinity icon button** (`lucide-react: Infinity`):
  - Click → clears input value, sends `null` to backend → "Unlimited"
  - Tooltip: "Set Unlimited"
  - Active state: button highlighted when unlimited
- **Backend value**: `Optional[int]` — value or `None` (unlimited)
- **Default**: Public → Unlimited, Private → 1 attempt
- **Description**: "0 attempts means test can only be viewed, not taken" — clarify separately if needed

### Track completion time
| Аспект | Детали |
|---|---|
| Type | Toggle (Yes/No) |
| Label | Track completion time |
| Default | Enabled |

### Tags

Комбинированный input + dropdown:

1. Показывает текущие теги как chips с ✕
2. При вводе текста — search существующих тегов (GET `/tags?q=...`)
3. Dropdown с результатами
4. Если нет совпадений — "Create tag \"xyz\"" option
5. Максимум — без ограничений

### Completion screen

| Аспект | Детали |
|---|---|
| Toggle | Enable/disable custom completion screen |
| Messages (if enabled) | Three Typst textareas for score ranges: 100-80%, 79-50%, <50%. Each supports `#score`, `#max_score`, `#percent` variables |
| Media (if enabled) | Media upload component per range (max 10 files each). Displayed on completion screen matching the user's score range |

**Behavior:** When the completion screen is enabled, three message+media blocks are shown. When disabled, no custom completion UI is rendered.

## Actions

| Действие | Триггер | Результат |
|---|---|---|
| Save | Click "Save Changes" | PATCH `/tests/:id` with all fields |
| Cancel | Click "Cancel" | Navigate back to `/tests/:id` |
| Delete test | Link in bottom "Delete test" | DELETE `/tests/:id` → redirect `/my-tests` |
| Change cover | Click cover image section | Upload to MinIO → update test |
| Remove cover | Click "Remove" | Clear cover_url |

## States

| State | Визуал |
|---|---|
| Loading | Form skeleton |
| Saving | Button disabled + spinner |
| Save error | Toast "Failed to save" |
| Delete confirm | Dialog "Are you sure? This cannot be undone." |
| Saved | Toast "Saved" → maybe auto-navigate back |
