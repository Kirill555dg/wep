# Results — `/attempts/:attemptId`

Results page for a specific test attempt. Uses the same two-column layout as the test content template (take/edit modes): a 240px side panel on the left, and a scrollable main question area on the right. No modals — all question detail is shown inline.

---

## Two-Column Layout

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Top bar                                                                 │
│├───────────────────────────────────────────────────────────────────────┤│
│                                                                         │
│ ┌──────────┐  ┌───────────────────────────────────────────────────────┐│
│ │          │  │                                                       ││
│ │  Q1  Determinant                                 [1/1]  ││
│ │                                              + ───────││
│ │  Q2  Solve for x                              [0/1]   ││
│ │                                              + ───────││
│ │  Q3  Vector match                             [2/2]   ││
│ │                                              + ───────││
│ │  Q4  Matrix rank                              [1/1]   ││
│ │                                              + ───────││
│ │                                                     .  ││
│ │          │  │                                                       ││
│ │          │  │        What is $det(A)$ for matrix $A$?              ││
│ │          │  │                                                       ││
│ │          │  │        ┌─────────────────────────────────┐           ││
│ │          │  │        │  Typst-rendered question         │           ││
│ │          │  │        │  (read-only, native scaling)     │           ││
│ │          │  │        └─────────────────────────────────┘           ││
│ │          │  │                                                       ││
│ │  SCORE   │  │        Media: [diagram.png] (read-only)              ││
│ │  10/15   │  │                                                       ││
│ │          │  │        Your answer:                                   ││
│ │  CORRECT │  │        +-----++-----+                                 ││
│ │  7/12    │  │        |  a·d  |  -b·c  |  (selected blocks marked)  ││
│ │          │  │        +-----++-----+                                 ││
│ │  TIME    │  │                                                       ││
│ │  23m 14s │  │        Correct answer:                                ││
│ │          │  │        a·d − b·c                                      ││
│ │          │  │                                                       ││
│ │          │  │        +------+                                       ││
│ │          │  │        |  1pt  |  (points earned / max)              ││
│ │          │  │        +------+                                       ││
│ │          │  │                                                       ││
│ │          │  │        Explanation:                                   ││
│ │          │  │        The determinant of [[a,b],[c,d]] is a·d − b·c.││
│ │          │  │                                                       ││
│ └──────────┘  └───────────────────────────────────────────────────────┘│
│                                                                         │
│ (scrollable independently in each column)                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Side Panel (240px)

### Question list

Each row is clickable. Background color encodes correctness:

```
┌──────────────────────┐
│                      │
│  [green bg]  Q1  Determinant                    1/1     │
│                      │
│  [red   bg]  Q2  Solve for x                     0/1     │
│                      │
│  [green bg]  Q3  Vector match                   2/2     │
│                      │
│  [green bg]  Q4  Matrix rank                    1/1     │
│                      │
│  ... (scrollable)    │
│                      │
│                      │
│  ──────────────────  │
│                      │
│  Score:        10/15 │
│  Correct:     7/12   │
│  Time:      23m 14s │
│                      │
│  (no [Retake] button │
│   on this page)      │
│                      │
└──────────────────────┘
```

### Per-question row

```
┌──────────────────────────────────┐
│                                  │
│  ┌────────┐  Short name    N/N   │
│  | Q#     |                     │
│  └────────┘  Truncated if long   │
│                                  │
└──────────────────────────────────┘
```

| Element | Notes |
|---|---|
| Background | Green (`bg-green-100` / equivalent) if `is_correct == true`; red (`bg-red-100`) if false |
| Question number | `Q1`, `Q2`, etc. |
| Short name | Truncated with ellipsis if longer than ~18 chars |
| Points | `earned / max` (e.g. `1/1`, `0/2`) |
| Click | Selects this question; main area scrolls to / renders it |
| Active state | Slightly darker border or ring to show currently-selected question |

### Bottom statistics

```
┌──────────────────────┐
│  Score:       10/15  │
│  Correct:     7/12   │
│  Time:     23m 14s   │
│                      │
│  NO [Retake Test]    │
│  button here.        │
└──────────────────────┘
```

| Field | Source |
|---|---|
| Score | `attempt.score` / `attempt.max_score` |
| Correct | Count of `is_correct == true` / total questions |
| Time | `attempt.time_spent` formatted as `Xm Ys` |
| Retake button | **NOT shown** — only on `/tests/:testId` page |

---

## Main Question Area

### Static (read-only) question card

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Question N / Total                                              │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                                                            │  │
│  │  Typst-rendered question (read-only)                       │  │
│  │                                                            │  │
│  │  (native browser scaling only)                             │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Media: [diagram.png]   [matrix.svg]   (read-only carousel)      │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### User answer section

Shows exactly what the user submitted, with selections/inputs marked but disabled:

**For choice / matching:**
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Your answer:                                                    │
│                                                                  │
│  +-----+  +-----+  +-----+                                       │
│  |  A  |  |  B  |  |  C  |   <- selected blocks highlighted    │
│  +-----+  +-----+  +-----+                                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**For text input:**
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Your answer:                                                    │
│  ┌────────────────────────────────────┐                          │
│  │  42                                 │   (disabled text field)   │
│  └────────────────────────────────────┘                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

**For file upload:**
```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Your answer:                                                    │
│  [📄 solution.pdf]  (read-only file preview or name)             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Correct answer section

Shown for every question type where a correct answer exists:

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Correct answer:                                                 │
│  a·d − b·c                                                       │
│                                                                  │
│  +------+                                                        │
│  |  1pt |   Points earned / max points                          │
│  +------+                                                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Notes |
|---|---|
| Correct answer | Rendered in the same style as the question type (choice blocks, plain text, etc.) |
| Points badge | Green if `earned == max`; gray otherwise |

### Explanation

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Explanation:                                                    │
│  The determinant of [[a,b],[c,d]] is calculated as a·d − b·c.     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

Only shown when `question.explanation` is present.

---

## Navigation Flow

```
(Results page loads)
         |
         v
   Completion screen configured?
         |
    +----+----+
    |         |
   Yes        No
    |         |
    v         v
 Show overlay   Show results
 (one time)     immediately
    |
    v
 [View Results] or close
    |
    v
  Results view (same layout as test template)
    |
    +-- click question in side panel --> render that question inline
```

### Completion screen overlay

Same component as described in `06-test-content-template.md`. Rendered on top of the results page when a completion message is configured and the user has not yet dismissed it:

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  (Typst-rendered completion message)                       │  │
│  │                                                            │  │
│  │  Great job! You scored 12 out of 15!                       │  │
│  │                                                            │  │
│  │  Media: [confetti animation]                               │  │
│  │                                                            │  │
│  │  [View Detailed Results]                                   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  (dimmed background; results page visible underneath)            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| Element | Behavior |
|---|---|
| Overlay | Centered modal-like card on a dimmed backdrop |
| Dismiss | `[View Detailed Results]` button, or clicking outside |
| One-time | Dismissal tracked per `attemptId` (localStorage flag) |

---

## State & Interactions

| Action | Trigger | Result |
|---|---|---|
| Select question | Click row in side panel | Main area renders that question's detail inline |
| Scroll question | Scroll main area | Independent from side panel scroll |
| Zoom Typst | Native browser scaling only (`Ctrl/Cmd +/-`) | Same as template — no UI controls, native scaling only |
| View media | Click carousel thumbnail | Same carousel component as test content template |
| Dismiss completion | Click `[View Detailed Results]` or outside | Hide overlay, show full results; set localStorage flag |

---

## Comparison with Take / Edit Modes

| Feature | Take mode | Edit mode | Results mode |
|---|---|---|---|
| Side panel width | 240px | 240px | 240px |
| Side panel items | Question numbers | Question numbers | Question numbers + score + correctness color |
| Main area | Active question (interactive) | Active question (interactive) | Selected question (read-only) |
| Answer interaction | Editable | Editable | Disabled / highlighted |
| Correct answer | Hidden | Hidden (preview shows) | Shown |
| Explanation | Hidden | Hidden (preview shows) | Shown |
| Points | Not shown | Not shown | Shown |
| Navigation prev/next | Shown | Shown | Not shown (side panel only) |
| Timer | Shown | Hidden | Hidden; time spent shown in side panel bottom |
| [Submit] / [Save] | Shown | Shown | Hidden |

---

## Key Points

- Uses the exact same two-column layout component as the test content template.
- Side panel uses color to communicate correctness at a glance (green = correct, red = wrong).
- Bottom of side panel displays attempt-level summary stats; no [Retake Test] button here.
- Main area is read-only: all inputs disabled, all answers displayed as static content.
- Correct answer is always visible in results mode.
- Explanation shown when available.
- No modals: clicking a question in the side panel replaces the main area content inline.
- Completion screen overlay (if configured) is shown first; once dismissed, the standard results view is revealed.
