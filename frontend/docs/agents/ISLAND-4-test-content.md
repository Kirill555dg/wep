# ISLAND-4: Test Content — Unified Take / Edit / Review Template

## Goal

Build the **unified content template** — the core UI for taking, editing, and reviewing
test questions. All three modes share the same layout; differences are minimal.

## Design reference (CRITICAL)

`docs/dev/frontend/06-test-content-template.md` — 825 lines, the most important design document.

Key visual principle: **same layout for all modes**.

```
+------------------------+  +------------------------------------------+
| Side Panel  (240px)    |  | Main area (vertical stack)                |
|                        |  |                                          |
| Questions list         |  |  1. Typst render (top)                  |
| [navigable]            |  |     — read-only in all modes            |
|                        |  |                                          |
| (Edit: + Add button)   |  |  2. Media carousel (middle, if any)    |
|                        |  |     — view-only in take/review          |
| (Review: colored rows  |  |     — editable in edit: drag/drop/add  |
|  + points shown)       |  |                                          |
|                        |  |  3. Answer area (bottom)                |
+------------------------+  |     — take: interactive                 |
                            |     — edit: inline editable             |
                            |     — review: highlighted correct/wrong |
                            |                                          |
                            |  4. [Prev] [Next] navigation            |
                            +------------------------------------------+
```

No zoom UI for Typst. Native browser scaling only (`Ctrl+` / `Ctrl-`).

## Files to modify / create

| File | Action |
|---|---|
| `src/pages/test-content/TakeTestPage.tsx` | Replace placeholder — main mode router (take/edit/review) |
| `src/widgets/question-panel/` | Create — 240px side panel with question list |
| `src/shared/components/TypstRender.tsx` | Create — renders Typst source to SVG/ HTML |
| `src/shared/components/MediaCarousel.tsx` | Create — 0-10 items, type-aware display |
| `src/shared/components/AnswerBlocks.tsx` | Create — single/multiple/text/file/match blocks |
| `src/pages/test-content/TypstEditorPage.tsx` | Create — sub-page for live Typst editing |

### Route usage

| Route | Purpose |
|---|---|
| `/tests/:testId/take` | User answers questions |
| `/tests/:testId/edit` | Author edits questions inline |
| `/attempts/:attemptId` | Review finished attempt (results) |
| `/tests/:testId/questions/:questionId/typst` | Live Typst source editing sub-page |

The `TakeTestPage` component accepts `editMode` prop to switch between take and edit.

## Component architecture

```
TestContentPage (mode: 'take' | 'edit' | 'review')
├── useContentState      (currentQuestionIndex, answers cache, etc.)
├── Top bar (mode-specific)
│   ├── take: [Back] Title Timer Q# / Total
│   ├── edit: [Back] Title [Settings] [Add from pool]
│   └── review: [Back] Title Score
├── QuestionPanel (240px)
│   ├── QuestionList
│   │   └── QuestionRow (clickable, colored in review)
│   ├── EditActions       (only edit)
│   │   ├── [+ Add Question]
│   │   └── [Add from pool]
│   └── ReviewStats       (only review)
│       ├── Total score
│       ├── Correct count
│       └── Time spent
└── MainArea
    ├── TypstRender
    │   └── (edit: has [Edit Typst] button → TypstEditorPage)
    ├── MediaCarousel (if media.length > 0)
    │   ├── Take/review: view-only chips
    │   └── Edit: drag-drop zone + add/remove
    └── AnswerArea
        ├── Take: interactive blocks / inputs
        └── Edit: inline inputs + type selector
```

### 1. QuestionPanel (side panel, 240px)

```tsx
interface QuestionPanelProps {
  questions: QuestionResponse[]
  currentIndex: number
  onSelect: (index: number) => void
  mode: 'take' | 'edit' | 'review'
  // take: answered status
  answers?: Record<string, unknown>
  // review: correctness & points
  results?: Record<string, { isCorrect: boolean; pointsEarned: number; maxPoints: number }>
}
```

Row states:
- `current`: primary background, left border highlight
- `answered` (take): checkmark icon
- `correct` (review): green background, checkmark
- `wrong` (review): red background, X mark + `0/2 pts`
- `unanswered`: empty circle

Edit mode additional actions:
- `[+ Add Question]` → POST new empty question → navigate to it
- `[Add from pool]` → open dialog of existing questions (author's test pool)
- Drag handle on each question → reorder → PATCH test order

### 2. TypstRender

```tsx
interface TypstRenderProps {
  source: string   // raw Typst source text
}
```

- Uses `@myriaddreamin/typst.ts` (already in project via vite-plugin-wasm).
- Renders to SVG or HTML.
- No zoom UI. Container: `w-full`, basic padding.
- If overflow `max-h-[50vh]` with `overflow-y-auto`.
- Edit mode only: show `[✎ Edit]` button near the render.
  - Button tooltip: "Edit in live view"
  - Click: `navigate('/tests/:testId/questions/:questionId/typst')`

### 3. MediaCarousel

```tsx
interface MediaCarouselProps {
  files: MediaFile[]
  mode: 'take' | 'edit' | 'review'
}

interface MediaFile {
  id: string
  url: string
  type: 'image' | 'audio' | 'video'
  filename: string
}
```

Max 10 items. Displayed as chips above the content area:
```
[🏞 1/3] [🎵 2/3] [📹 3/3]
```

Active chip highlighted. Below chips: media preview area.

| Type | Preview component |
|---|---|
| image | `<img>` object-fit: contain |
| audio | `<audio controls>` |
| video | `<video controls>` |

Edit mode extra features:
- Drag-and-drop zone below chips
- Each item has `✕` remove button
- `[+ Add Media]` button opens file picker
- Max 10 files enforced
- Auto-detect file type by MIME after upload

### 4. AnswerArea

Single component that renders different input types based on `question.question_type`.

**Single Choice:**
- Blocks with Typst-rendered text (via `TypstRender` component using `source={option.text}`).
- Layout auto: horizontal row (1-3) → 2 columns (even) → 1 column fallback.
- Click to select (last click wins). Click selected to deselect.
- Max 8 options.

**Multiple Choice:**
- Same blocks but checkboxes (`☑` / `☐` style).
- Click toggles multiple selections.

**Text (free input):**
- `<textarea>` with auto-resize.
- No format buttons (plain text).

**File Upload (for student):**
```
📁 Drag & drop or click to upload
Supported: .pdf .txt .py .zip etc.

[Optional comment:]
[__________________]
```
- Only shown if author configured this question as file-upload
- Comment textarea optional

**Matching (future / feature-request):**
Not implemented yet. If type is matching, show placeholder.

**Edit mode extras:**
- `Type: [Single ▾] Points: [1^]` — inline selector and number input
- Each option text is `input` (rendered as Typst in preview, raw text in edit)
- Checkbox `✅ correct?` per option
- Drag handle ⇅ to reorder
- `[+ Add option]` (max 8)
- `Explanation:` inline textarea (shown after question in review)

### 5. TypstEditorPage (live-render sub-page)

```
┌────────────────────────────────────────────────┐
│  ← Back                Typst Editor            │
├────────────────────────────────────────────────┤
│  ┌────────── Source ──────────┐ ┌── Render ──┐│
│  │                             │ │            ││
│  │  What is $det(A)$?          │ │  (SVG)     ││
│  │  for matrix $A$?            │ │            ││
│  │                             │ │            ││
│  └─────────────────────────────┘ └────────────┘│
│  Status: ✅ Valid / ❌ Error at line 3          │
│  [Save & Close]                                  │
└────────────────────────────────────────────────┘
```

- Split pane (50/50) or modal-like overlay
- Left: `<textarea>` with raw Typst source
- Right: live rendered preview with debounce 500ms
- Status line showing parse errors
- Save → PATCH question text → navigate back

## State management

### Take mode

```tsx
const [currentIndex, setCurrentIndex] = useState(0)
const cache = useAttemptCache(testId)

// On every answer interaction:
const handleAnswer = (questionId: string, type: string, value: unknown) => {
  cache.updateAnswer(questionId, type, value)
}
```

### Edit mode

```tsx
const [questions, setQuestions] = useState<QuestionAuthorResponse[]>([...])

// Auto-save after each change (debounce 2s):
useDebounce(() => {
  patchQuestion(testId, currentQuestion.id, dirtyFields)
}, 2000, [dirtyFields])
```

### Review mode

```tsx
const { attemptId } = useParams()
const { data: attempt } = useQuery({
  queryKey: ['attempt', attemptId],
  queryFn: () => getResultApiV1AttemptsAttemptIdResultGet({
    client, path: { attempt_id: Number(attemptId) }
  }),
})
```

## API endpoints (done)

| Endpoint | SDK Function | Purpose |
|---|---|---|
| `GET /tests/:id/questions` | via `getTestApiV1TestsTestIdGet` | Load questions |
| `POST /attempts` | `startAttemptApiV1AttemptsPost` | Start new attempt |
| `GET /attempts/:id` | `getAttemptApiV1AttemptsAttemptIdGet` | Get attempt info |
| `GET /attempts/:id/result` | `getResultApiV1AttemptsAttemptIdResultGet` | Graded results |
| `POST /attempts/:id/finish` | `finishAttemptApiV1AttemptsAttemptIdFinishPost` | Finish + grade |
| `POST /attempts/:id/answers` | `submitAnswerApiV1AttemptsAttemptIdAnswersPost` | Send one answer |
| `POST /tests/:id/questions` | `addQuestionApiV1TestsTestIdQuestionsPost` | Add question |
| `PATCH /tests/:id/questions/:qid` | `updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch` | Update question |
| `DELETE /tests/:id/questions/:qid` | `deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete` | Delete question |
| `POST /media/upload` | `uploadMediaApiV1MediaUploadPost` | Upload media file |

## Verification checklist

- [ ] Build passes
- [ ] Side panel shows question list, current is highlighted
- [ ] Typst renders correctly in main area
- [ ] Media carousel works (view/add/remove depending on mode)
- [ ] Answer blocks are interactive in take mode
- [ ] Auto-save works in edit mode (debounced)
- [ ] Review mode shows correct/wrong colors + points
- [ ] Typst editor sub-page renders live preview
- [ ] Prev/Next navigation works
- [ ] CTA [Submit All] finalizes attempt and navigates to `/attempts/:id`

## Design file

`docs/dev/frontend/06-test-content-template.md` — the single most important design document.

## Related islands

- **ISLAND-3 (Test View)** — for [Start Test] navigation
- **ISLAND-5 (Results)** — review mode is the same template
- **ISLAND-1 (Catalog)** — back link
