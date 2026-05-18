# ISLAND-5: Results Page (`/attempts/:attemptId`)

## Goal

Build the **results page** — review a completed test attempt.
Uses the **same unified layout** as the test content template (take/edit),
but in read-only mode with correctness highlighting.

## Design reference

`docs/dev/frontend/09-results.md`

Key visual:
- Same 240px side panel + main area vertical stack layout as ISLAND-4
- Side panel shows color-coded question list (green=correct, red=wrong)
- Bottom of side panel: total score, correct count, time spent
- Main area: question + user answer + correct answer + explanation
- Click question in panel → shows details inline (no modals)
- No [Retake] button (that's only on `/tests/:id`)

## Files to modify

| File | Action |
|---|---|
| `src/pages/results/ResultsPage.tsx` | Replace placeholder |

## Component architecture

```
ResultsPage
├── TopBar (mode-specific)
│   └── Score: X/Y + attempt #
├── QuestionPanel (240px)
│   ├── QuestionList
│   │   └── QuestionRow
│   │       ├── correct → green bg + ✅
│   │       ├── wrong → red bg + ❌ + "0/2"
│   │       └── unanswered → neutral
│   └── ReviewStats
│       ├── Total: X/Y
│       ├── Correct: N questions
│       └── Time: 23m 14s
└── MainArea (read-only)
    ├── TypstRender
    ├── MediaCarousel (view-only)
    ├── UserAnswerDisplay
    │   ├── For choice: highlighted selected block (red/green border)
    │   ├── For text: textarea content
    │   └── For file: file name + comment
    ├── CorrectAnswerDisplay
    │   └── Correct blocks highlighted in green
    └── Explanation (if present)
```

### Data

```tsx
const { attemptId } = useParams()

const { data: result } = useQuery({
  queryKey: ['attempt', attemptId],
  queryFn: () => getResultApiV1AttemptsAttemptIdResultGet({
    client,
    path: { attempt_id: Number(attemptId) }
  }),
})
```

Result structure: `AttemptResultResponse`.

Key fields:
- `score`, `max_score`
- `status` ('completed' | 'expired' | 'abandoned')
- `started_at`, `finished_at`
- `answers: AttemptAnswerDetail[]`

Each answer detail:
- `question_id`, `question_text`, `question_type`, `points`
- `selected_option_ids`, `text_answer`, `is_correct`, `points_earned`
- `correct_option_ids`, `explanation`

### State

```tsx
const [currentIndex, setCurrentIndex] = useState(0)
const currentQuestion = result.answers[currentIndex]
```

### QuestionRow in side panel

Each row must show:
- Icon/number
- Short question name (title if present, otherwise "Question N")
- Points earned / max: `1/1` or `0/2`
- Background color:
  - `bg-green-50` if `is_correct === true`
  - `bg-red-50` if `is_correct === false`
  - `bg-gray-50` if unanswered

### Main area content

For the current question:
1. **Typst render** of `question_text`
2. **Media** if any (using same `MediaCarousel` as ISLAND-4, read-only)
3. **User's answer** — rendered using same `AnswerBlocks` component but with `readonly` prop
4. **Correct answer** — shown clearly below user's answer
   - For multiple choice: all correct options highlighted green
   - For text: correct text shown in a box
   - For file: "Requires manual review" if `is_correct` is null
5. **Explanation** — if present, shown in a prose block
6. **Points badge** — `+1 pt` (green) or `0 pts` (gray)

### Completion screen overlay

If the test has `completion_message` configured and this is the first time viewing this attempt:

```tsx
const [showOverlay, setShowOverlay] = useState(
  !localStorage.getItem(`finished_${attemptId}`)
)
useEffect(() => {
  if (showOverlay) {
    localStorage.setItem(`finished_${attemptId}`, '1')
  }
}, [showOverlay])
```

Overlay content:
- Typst-rendered message (from test settings)
- Media (if any)
- `[View Results]` button → dismiss overlay

## Verification checklist

- [ ] Build passes
- [ ] Fetches attempt result correctly
- [ ] Side panel shows correctness colors
- [ ] Click question in panel → renders details inline
- [ ] Correct answer is always visible in main area
- [ ] Explanation shown when present
- [ ] Completion screen overlay appears once per attempt (tracked via localStorage)
- [ ] No [Retake] button on this page
- [ ] `[Back to History]` link at top

## Design file

`docs/dev/frontend/09-results.md`

## Related islands

- **ISLAND-4 (Test Content)** — same layout, same components
- **ISLAND-6 (History)** — back link destination
- **ISLAND-1 (Catalog)** — if user navigates away
