# Test Content Template

Single unified layout for **Take**, **Edit**, and **Review** modes.
Differences between modes are minimal: edit mode swaps static text for inline inputs; review mode adds correctness styling and disables interaction.

---

## 1. Global Layout

```
+------------------------------------------------------------------+
|  Top bar (mode-specific content)                                  |
|------------------------------------------------------------------|
|                                                                  |
|  +----------+  +----------------------------------------------+ |
|  |          |  |                                              | |
|  |  Side    |  |  Main content area (vertical stack)          | |
|  |  Panel   |  |                                              | |
|  |  240px   |  |  +----------------------------------------+  | |
|  |          |  |  |  Typst render (top)                    |  | |
|  |          |  |  |  - no zoom UI                         |  | |
|  |          |  |  |  - browser native scale only          |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |  |                                        |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |  |  Media carousel (middle, if any)       |  | |
|  |          |  |  |  - max 10 items                        |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |  |                                        |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |  |  Answer area (bottom)                  |  | |
|  |          |  |  |  - selectable blocks                   |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |  |                                        |  | |
|  |          |  |  |  [<- Prev]              [Next ->]       |  | |
|  |          |  |  |  [Submit All] (take only)               |  | |
|  |          |  |  +----------------------------------------+  | |
|  |          |  |                                              | |
|  +----------+  +----------------------------------------------+ |
|                                                                  |
+------------------------------------------------------------------+
```

- Side panel is always fixed at **240px** on the left.
- Main area is a **vertical stack**:
  1. Typst render (top)
  2. Media carousel (middle, only if present)
  3. Answer area (bottom)
- **No manual zoom controls** for Typst. Native browser scaling (`Ctrl/Cmd + +/-`, pinch) is the only way to zoom.
- Answers are always at the **bottom** of the main area.

---

## 2. Routes

| Mode | Route | Purpose |
|------|-------|---------|
| Take | `/tests/:testId/take` | User answers questions |
| Edit | `/tests/:testId/edit` | Author edits questions inline |
| Review | `/attempts/:attemptId` | Review results after submission |
| Typst Live Render | `/tests/:testId/questions/:questionId/typst` | Split-pane Typst editor/preview (separate sub-page) |

---

## 3. Top Bar

### Take Mode

```
+------------------------------------------------------------------+
|  <- Back    Test Title                    Timer    Question 4/15  |
|  (return)                                 (mm:ss)  (progress)      |
+------------------------------------------------------------------+
```

### Edit Mode

```
+------------------------------------------------------------------+
|  <- Back    Test Title                    [Settings]  [Add from...]|
|  (return)                                 (link)      (reuse pool) |
+------------------------------------------------------------------+
```

### Review Mode

```
+------------------------------------------------------------------+
|  <- Back    Test Title                    Score: 12/15  Attempt #2|
|  (return)                                          (attempt info) |
+------------------------------------------------------------------+
```

---

## 4. Side Panel (240px, all modes)

```
+--------------------------------------+
|  Questions                           |
|  ----------------------------------  |
|                                      |
|  Take mode:                          |
|  [o] 1. Question 1          [done]   |
|  [o] 2. Question 2          [open]   |
|  [o] 3. Question 3          [done]   |
|  [o] 4. Question 4          [open]   |
|  [o] 5. Question 5          [open]   |
|                                      |
|  Edit mode:                          |
|  [o] 1. Question 1     [edit] [del]  |
|  [o] 2. Question 2     [edit] [del]  |
|  [o] 3. Question 3     [edit] [del]  |
|  [o] 4. [empty slot]                 |
|  [o] 5. Question 5     [edit] [del]  |
|                                      |
|  [+ Add Question]    (edit only)     |
|  [Add from pool]     (edit only)     |
|                                      |
|  Review mode:                        |
|  [v] 1. Question 1     1/1 pt        |
|  [x] 2. Question 2     0/2 pts       |
|  [v] 3. Question 3     1/1 pt        |
|  [x] 4. Question 4     0/1 pt        |
|  [~] 5. Question 5     0/0 pts       |
|                                      |
|  --- Total Stats (review only) ---   |
|  Score: 12/15 (80%)                 |
|  Correct: 3  Wrong: 2  Unanswered: 0|
+--------------------------------------+
```

### Panel Item States

| State | Visual |
|-------|--------|
| Current question | Primary tint background, left border highlight |
| Answered (take) | Checkmark or filled indicator |
| Unanswered (take) | Empty circle |
| Correct (review) | Green accent, checkmark, points earned shown |
| Wrong (review) | Red accent, cross, points 0 shown |
| Unanswered (review) | Neutral, 0 points |
| Empty slot (edit) | Dashed border, clickable to add |

### Panel Actions (Edit Mode)

| Action | Behavior |
|--------|----------|
| Click question row | Navigate to that question |
| Click [edit] icon | Open Typst live-render sub-page for this question |
| Click [del] icon | Delete question (with confirmation) |
| Drag handle | Reorder questions via drag-and-drop |
| Click [+ Add Question] | Create new empty question at end, navigate to it |
| Click [Add from pool] | Open question pool browser (reuse existing) |

---

## 5. Question Area — Vertical Stack

### 5.1 Typst Render Area (top)

```
+--------------------------------------------------------------+
|  Typst render area                                           |
|                                                              |
|  #prob.bold[Question 4]  (title, if set)                    |
|                                                              |
|  What is the determinant of a 2x2 matrix                    |
|  $det(A) = a d - b c$                                       |
|                                                              |
|  (if content exceeds max-height: scroll Y)                  |
|                                                              |
|  [Open Typst Editor]  (button with tooltip: "Edit Typst...")|
|                                                              |
+--------------------------------------------------------------+
```

- **No zoom UI**: no slider, no +/- buttons, no percentage display.
- Zooming is done via **native browser scaling** only (keyboard shortcuts, pinch, OS zoom).
- A button "Open Typst Editor" (with tooltip) navigates to the separate Typst live-render sub-page at `/tests/:testId/questions/:questionId/typst`.
- Content overflows with vertical scroll.

#### Typst Render Properties

| Property | Value |
|----------|-------|
| Min height | 200px |
| Max height | 50vh |
| Scroll | overflow-y: auto |
| Font size (default body) | 16pt |
| Zoom controls | None (native browser only) |

---

### 5.2 Media Carousel (middle, if present)

```
+--------------------------------------------------------------+
|  Media carousel (0 to 10 items)                              |
|                                                              |
|  [img 1/3]  [aud 2/3]  [vid 3/3]  [img 4/4]                 |
|                                                              |
|  +--------------------------------------------------------+  |
|  |                                                        |  |
|  |  Media preview area                                   |  |
|  |  - image: fit with contain, max-height 300px           |  |
|  |  - audio: native audio player controls                |  |
|  |  - video: native video player controls, max-h 300px   |  |
|  |                                                        |  |
|  +--------------------------------------------------------+  |
|                                                              |
+--------------------------------------------------------------+
```

- **Max 10 files** per question.
- **Auto-detect type by MIME** on upload.
- Displayed as a **carousel** below the Typst area.
- Each item is a chip with type label and index.
- Active chip is highlighted.
- If no media is attached, this section is **hidden entirely**.

#### Media Type Display

| MIME type prefix | Component |
|------------------|-----------|
| image/* | `<img>` with object-fit: contain, max-height 300px |
| audio/* | `<audio controls>` |
| video/* | `<video controls>` with max-height 300px |

#### Media Controls (Edit Mode)

```
[img file1.png X]  [aud file2.mp3 X]  [vid file3.mp4 X]  [+ Add]
(Drag and drop zone below chips)
```

- Drag-and-drop zone to add files.
- [X] removes the file.
- [+ Add] opens a file picker.
- Auto-detect type on upload via MIME.
- Backend enforces file size limits.

---

### 5.3 Answer Area (bottom)

All answer options are **Typst-rendered text inside selectable blocks**.

#### Adaptive Layout Rules

| Condition | Layout |
|-----------|--------|
| 1 to 3 options AND sufficient width | Single row (horizontal) |
| Even count (2, 4, 6, 8) | 2 columns (grid) |
| Space insufficient (narrow viewport) | 1 column (stacked) |
| Max options | 8 |

```
+--------------------------------------------------------------+
|  Answer area (adaptive layout)                               |
|                                                              |
|  1-3 options (single row, if fits):                          |
|  +----------------+  +----------------+  +----------------+ |
|  | Option A       |  | Option B       |  | Option C       | |
|  +----------------+  +----------------+  +----------------+ |
|                                                              |
|  Even count (2 columns):                                     |
|  +------------------------+  +------------------------+      |
|  | Option A               |  | Option B               |      |
|  +------------------------+  +------------------------+      |
|  +------------------------+  +------------------------+      |
|  | Option C               |  | Option D               |      |
|  +------------------------+  +------------------------+      |
|                                                              |
|  Narrow or many (1 column):                                  |
|  +----------------------------------------------------+     |
|  | Option A                                           |     |
|  +----------------------------------------------------+     |
|  +----------------------------------------------------+     |
|  | Option B                                           |     |
|  +----------------------------------------------------+     |
|                                                              |
+--------------------------------------------------------------+
```

#### Block Interaction States

| State | Visual |
|-------|--------|
| Default | Light background, subtle border, Typst-rendered text centered/left-aligned |
| Hover | Slightly darker background, pointer cursor |
| Selected | Primary tint background, primary border, primary text color |
| Correct (review) | Green tint background, green border, checkmark icon |
| Wrong selected (review) | Red tint background, red border, cross icon |

---

## 6. Question Types

### 6.1 SINGLE_CHOICE

```
+--------------------------------------------------------------+
|  Type: Single Choice    Points: +1                           |
|                                                              |
|  +------------------------+                                  |
|  |  $a d - b c$          |  <- selected (last clicked)       |
|  +------------------------+                                  |
|  +------------------------+                                  |
|  |  $a b - c d$          |                                   |
|  +------------------------+                                  |
|  +------------------------+                                  |
|  |  $a + d$              |                                   |
|  +------------------------+                                  |
|  +------------------------+                                  |
|  |  $a d + b c$          |                                   |
|  +------------------------+                                  |
+--------------------------------------------------------------+
```

- **Click block** to select it.
- **Click selected block** to deselect (no selection).
- Only **one** option can be selected at a time. Last clicked wins.
- In review mode: highlight correct answer in green, selected wrong answer in red.

### 6.2 MULTIPLE_CHOICE

```
+--------------------------------------------------------------+
|  Type: Multiple Choice    Points: +2                         |
|                                                              |
|  +------------------------+  +------------------------+    |
|  |  [on]  $E = mc^2$    |  |  [off] $F = ma$        |    |
|  +------------------------+  +------------------------+    |
|  +------------------------+  +------------------------+    |
|  |  [on]  $a^2 + b^2 = c^2$ |  |  [off] $e^{i pi} = -1$ |    |
|  +------------------------+  +------------------------+    |
+--------------------------------------------------------------+
```

- **Click block** to toggle on/off.
- Multiple blocks can be selected simultaneously.
- In review mode: correct selections green, wrong selections red.

### 6.3 MATCHING

```
+--------------------------------------------------------------+
|  Type: Matching    Points: +4                                |
|                                                              |
|  Match each term with its definition:                        |
|                                                              |
|  +-------------------+    +---------------------------+    |
|  | Matrix            |    | A rectangular array...    |    |
|  +-------------------+    +---------------------------+    |
|         \__________ connected by line on match __________/   |
|                                                              |
|  +-------------------+    +---------------------------+    |
|  | Determinant       |    | A scalar value...         |    |
|  +-------------------+    +---------------------------+    |
|                                                              |
|  Interaction: click left item -> click right item to pair    |
|  Matched pairs highlighted with a connecting visual line     |
|                                                              |
+--------------------------------------------------------------+
```

- Left column: terms (fixed order).
- Right column: definitions (shuffled in take mode).
- Click left item, then click right item to form a pair.
- Click a paired item to unpair.
- In edit mode: inline inputs for terms and definitions, drag to reorder, [X] to remove pair, [+ Add Pair] (max 8 pairs).

### 6.4 TEXT (Free Input)

```
+--------------------------------------------------------------+
|  Type: Text    Points: +2                                    |
|                                                              |
|  Your answer:                                                |
|  +------------------------------------------------------+   |
|  |                                                      |   |
|  |  Type your answer here...                            |   |
|  |                                                      |   |
|  +------------------------------------------------------+   |
|                                                              |
|  (edit mode: Correct answer input shown below)               |
|  Correct answer: [______________________________]            |
+--------------------------------------------------------------+
```

- Large textarea for user input.
- Edit mode shows an additional "Correct answer" input field.

### 6.5 FILE_UPLOAD

```
+--------------------------------------------------------------+
|  Type: File Upload    Points: +1                             |
|                                                              |
|  Upload your solution:                                      |
|                                                              |
|  +------------------------------------------------------+   |
|  |                                                      |   |
|  |       [Drag & drop or click to upload a file]       |   |
|  |                                                      |   |
|  |       Supported: .pdf .txt .py .c .js .zip ...       |   |
|  |                                                      |   |
|  +------------------------------------------------------+   |
|                                                              |
|  Optional comment:                                          |
|  +------------------------------------------------------+   |
|  |                                                      |   |
|  |  Enter an optional comment about your submission...  |   |
|  |                                                      |   |
|  +------------------------------------------------------+   |
|                                                              |
+--------------------------------------------------------------+
```

- Drag-and-drop or click to select file.
- An **optional comment textarea** is provided below the drop zone.
- No "correct answer" in edit mode (requires manual review).

---

## 7. Inline Edit Mode

Edit mode uses the **same layout** as take/review, but fields become inline editable. No separate modal for editing a question.

```
+--------------------------------------------------------------+
|  Question title: [What is the determinant?______________]     |
|                                                              |
|  +------------------------------------------------------+   |
|  | Typst source input (textarea)                        |   |
|  | What is $det(A)$ for matrix $A$?                    |   |
|  +------------------------------------------------------+   |
|                                                              |
|  [Open Typst Editor]  (navigates to sub-page for live split)|
|                                                              |
|  (media carousel: same drag/drop/add/remove chips as above) |
|                                                              |
|  Type: [Single Choice v]    Points: [+1^]                 |
|                                                              |
|  Options (max 8):                                           |
|  +------------------------------+  [correct?]  [drag]  [X]  |
|  | [$a d - b c$_____________]  |   [x]        [=]    [X]  |
|  +------------------------------+                           |
|  +------------------------------+  [correct?]  [drag]  [X]  |
|  | [$a b - c d$_____________]  |   [ ]        [=]    [X]  |
|  +------------------------------+                           |
|  +------------------------------+  [correct?]  [drag]  [X]  |
|  | [$a + d$__________________]  |   [ ]        [=]    [X]  |
|  +------------------------------+                           |
|                                                              |
|  [+ Add Option]                                              |
|                                                              |
|  Explanation:                                               |
|  +------------------------------------------------------+   |
|  | The determinant of [[a,b],[c,d]] is a*d - b*c...     |   |
|  +------------------------------------------------------+   |
|                                                              |
+--------------------------------------------------------------+
```

- **Question title**: inline text input at the top.
- **Typst source**: inline textarea (live preview is available on the separate sub-page).
- **Options**: inline text inputs (Typst-rendered text), checkboxes for "correct", drag handles for reorder, [X] to delete.
- **Type and Points**: inline dropdown and number input.
- **Media**: inline carousel with add/remove.
- **Explanation**: inline textarea.
- Changes are **auto-saved** (see Section 9).

---

## 8. Typst Live Render Sub-page

Accessible via the "Open Typst Editor" button in the Typst render area (tooltip: "Edit Typst source in live preview mode").

**Route:** `/tests/:testId/questions/:questionId/typst`

```
+------------------------------------------------------------------+
|  <- Back to Question    Typst Editor    [Save & Close]          |
|  (return to test)                      (persists and returns)    |
|------------------------------------------------------------------|
|                                                                  |
|  +-----------------------------+  +---------------------------+ |
|  | Typst Source                |  | Live Preview              | |
|  |                           |  |                           | |
|  | What is $det(A)$          |  |                           | |
|  | for matrix $A$?           |  |  (rendered output         | |
|  |                           |  |   updates in real-time)   | |
|  |                           |  |                           | |
|  +-----------------------------+  +---------------------------+ |
|                                                                  |
+------------------------------------------------------------------+
```

- **Left pane**: Typst source textarea.
- **Right pane**: Live rendered preview.
- Updates are **live** (debounced 500ms while typing).
- [Save & Close] persists the source to the server (PATCH) and navigates back to the question page.
- This is a **separate sub-page**, not a modal.

---

## 9. State, Cache, and Auto-Save

### 9.1 Take Mode Cache (localStorage)

While taking a test, every answer change is immediately cached to **localStorage**.

| Event | Action |
|-------|--------|
| Select option in take mode | Write answer state to localStorage |
| Type in text field | Debounce 500ms, then write to localStorage |
| Match a pair | Write updated pairs to localStorage |
| Upload file + comment | Write metadata to localStorage (file itself is staged) |

**Key format:** `wep_test_take_<testId>_<attemptId>`

**Value:** JSON object with questionId -> answer mapping.

Only **submitted answers** are sent to the backend (POST/PATCH). Unsubmitted answers remain in localStorage only.

### 9.2 Resume Dialog

When navigating to `/tests/:testId/take`:

1. Check localStorage for a cached take state.
2. If found, show a dialog:
   ```
   +--------------------------------------+
   |  Resume Previous Session?            |
   |                                      |
   |  You have an unsaved progress for    |
   |  this test. Resume from where you    |
   |  left off?                           |
   |                                      |
   |  [Resume]        [Start Over]       |
   +--------------------------------------+
   ```
3. **Resume**: restore answers from localStorage, continue at last visited question.
4. **Start Over**: clear localStorage for this test/attempt, start fresh.

### 9.3 Edit Mode Auto-Save

Edit mode changes are **auto-saved** to the server with **debounce 2 seconds**.

| Action | Behavior |
|--------|----------|
| Input change | Debounce 2s, then PATCH question |
| Add/remove option | Immediate PATCH |
| Reorder options | Immediate PATCH |
| Media upload | Immediate POST/PATCH for file, then PATCH question |

PATCH endpoint: `PATCH /tests/:testId/questions/:questionId`

On PATCH failure, show a transient error toast (e.g., "Auto-save failed. Retry?").

---

## 10. Review Mode

Review mode uses the **same exact layout** as take and edit. Differences are visual, not structural.

### Side Panel in Review

```
+--------------------------------------+
|  Questions                           |
|  ----------------------------------  |
|                                      |
|  [V] 1. Question 1      1/1 pt (grn) |
|  [X] 2. Question 2      0/2 pts (red) |
|  [V] 3. Question 3      1/1 pt (grn) |
|  [X] 4. Question 4      0/1 pt (red) |
|  [~] 5. Question 5      0/0 pts (neu)|
|                                      |
|  ----------------------------------  |
|  Total Score: 12/15 (80%)           |
|  Correct: 3  Wrong: 2                |
|  Time spent: 18:45                   |
+--------------------------------------+
```

- Green = correct, Red = wrong, Neutral = unanswered/no points.
- Points earned shown next to each question.
- Bottom of panel: **total stats** (score, percentage, correct/wrong count, time spent).

### Main Area in Review

```
+--------------------------------------------------------------+
|  Question title (static)                                     |
|                                                              |
|  Typst render area (static, no edit controls)                |
|                                                              |
|  (media carousel, if any - static)                           |
|                                                              |
|  Answer area (read-only, shows user selection + correct)    |
|                                                              |
|  +------------------------+                                  |
|  |  $a d - b c$          |  <- correct answer (green)       |
|  +------------------------+                                  |
|  +------------------------+                                  |
|  |  $a b - c d$          |  <- your wrong pick (red)       |
|  +------------------------+                                  |
|  +------------------------+                                  |
|  |  $a + d$              |                                   |
|  +------------------------+                                  |
|                                                              |
|  Explanation:                                               |
|  +------------------------------------------------------+   |
|  | The determinant is calculated as ad - bc.            |   |
|  +------------------------------------------------------+   |
|                                                              |
|  [<- Prev]                            [Next ->]             |
+--------------------------------------------------------------+
```

- User's selected answers shown with correctness colors.
- Correct answers are always highlighted in green.
- Explanation is displayed below the answer area.
- All inputs are **disabled/read-only**.

---

## 11. Completion Screen Overlay

If the test settings have a completion screen configured:

```
+--------------------------------------------------------------+
|                                                              |
|  +------------------------------------------------------+   |
|  |                                                      |   |
|  |            Test Completed!                           |   |
|  |                                                      |   |
|  |    You scored 12 out of 15 points.                   |   |
|  |    Time spent: 18 minutes.                           |   |
|  |                                                      |   |
|  |    [View Results]        [Share]                      |   |
|  |                                                      |   |
|  +------------------------------------------------------+   |
|                                                              |
+--------------------------------------------------------------+
```

- Shown as an **overlay** after the user clicks "Submit All" and the attempt is finalized.
- Overlay blocks interaction until dismissed.
- [View Results] redirects to `/attempts/:attemptId` (review mode).
- If no completion screen is configured, redirect to results immediately.

---

## 12. Test Settings — Attempt Limits

Test settings control the number of attempts allowed.

| Visibility | Default Attempt Limit | Meaning |
|------------|-----------------------|---------|
| Public | ∞ (`null`) | **Unlimited** attempts (`null` means infinite) |
| Private | 1 | **One** attempt allowed |

### Configuration

- Backend: `attempt_limit: Optional[int]` — `None` means unlimited, `1` means one attempt.
- Frontend: beautiful toggle **"∞ Unlimited"** with optional number input when disabled.
- When user opens a test, check current attempts vs limit.
- If limit reached, show: "You have exhausted your attempts for this test."

---

## 13. Mode Comparison Table

| Aspect | Take | Edit | Review |
|--------|------|------|--------|
| **Answer area** | Interactive (click/toggle/drag) | Inline editable inputs | Read-only with correctness colors |
| **Side panel** | Question list + answered status | Question list + edit/delete/drag | Question list + correct/wrong + points + total stats |
| **Typst area** | Static render, [Open Editor] btn | Static render, [Open Editor] btn | Static render (no editor button) |
| **Media** | View-only carousel | Inline add/remove/drag-drop | View-only carousel |
| **Zoom controls** | None (native browser only) | None (native browser only) | None (native browser only) |
| **[+ Add Question]** | Hidden | Visible | Hidden |
| **[Add from pool]** | Hidden | Visible | Hidden |
| **[Edit] on questions** | Hidden | Icon in side panel | Hidden |
| **Type switch** | Hidden | Dropdown inline | Hidden |
| **Points input** | Hidden | Number input inline | Hidden |
| **Correct answer** | Hidden | Checkbox / input inline | Revealed in answer area |
| **Explanation** | Hidden | Inline textarea | Shown below answers |
| **Submit / Save** | [Submit All] button (finishes attempt) | Auto-save debounce 2s + PATCH | None |
| **Cache** | localStorage immediate | Server PATCH | None |
| **Resume dialog** | Shown if cache exists | N/A | N/A |
| **Completion overlay** | Shown after submit (if configured) | N/A | N/A |

---

## 14. Action Tables

### Answer Selection Actions (Take Mode)

| Action | State Before | State After | Side Effect |
|--------|--------------|-------------|-------------|
| Click option block (single) | Nothing selected | Block selected | Write to localStorage |
| Click option block (single) | Another selected | New block selected, old deselected | Write to localStorage |
| Click selected block (single) | Block selected | Nothing selected | Write to localStorage |
| Click option block (multiple) | Block unselected | Block selected | Write to localStorage |
| Click option block (multiple) | Block selected | Block unselected | Write to localStorage |
| Click left term (matching) | No active selection | Term marked as "waiting for pair" | - |
| Click right def (matching) | Left term waiting | Pair formed | Write to localStorage |
| Click paired item (matching) | Paired | Unpaired | Write to localStorage |
| Type in text input | - | Text changed | Debounce 500ms -> localStorage |
| Drop file / click upload (file) | No file | File staged | Write metadata to localStorage |
| Type in comment (file) | Empty | Comment text | Debounce 500ms -> localStorage |
| Click [Submit All] | Some answers cached | Attempt finalized, localStorage cleared | POST attempt to server |

### Edit Mode Actions

| Action | Behavior | Server Request |
|--------|----------|----------------|
| Type in question title | Debounce 2s | PATCH question |
| Type in Typst source | Debounce 2s | PATCH question |
| Add option | Insert new empty block | PATCH question (immediate) |
| Remove option | Remove block | PATCH question (immediate) |
| Toggle correct checkbox | Mark/unmark as correct | PATCH question (immediate) |
| Drag reorder options | Reorder in UI | PATCH question (immediate) |
| Change type dropdown | Switch answer area UI | PATCH question (immediate) |
| Change points input | Debounce 2s | PATCH question |
| Upload media file | Add to carousel | POST file, then PATCH question |
| Remove media file | Remove chip | DELETE file, then PATCH question |
| Click [Open Typst Editor] | Navigate to sub-page `/.../typst` | - |
| Click [Save & Close] in sub-page | Save source, return to question | PATCH question |
| Click [+ Add Question] | Create empty question, navigate | POST question |
| Click [del] in side panel | Confirm, delete question | DELETE question |
| Drag question in side panel | Reorder questions | PATCH test (order array) |

### Navigation Actions (All Modes)

| Action | Behavior |
|--------|----------|
| Click question in side panel | Navigate to that question index |
| Click [<- Prev] | Go to previous question (hidden on first) |
| Click [Next ->] | Go to next question (hidden on last) |
| Click <- Back in top bar | Return to parent page (test list / test detail) |

---

## 15. State Descriptions

### Take Mode State

```
take_state = {
  test_id: string,
  attempt_id: string | null,    // null until first submission
  current_question_index: number,
  answers: {
    [question_id: string]: {
      question_type: "SINGLE_CHOICE" | "MULTIPLE_CHOICE" | "MATCHING" | "TEXT" | "FILE_UPLOAD",
      // SINGLE_CHOICE: selected_option_id: string | null
      // MULTIPLE_CHOICE: selected_option_ids: string[]
      // MATCHING: pairs: { left_id: string, right_id: string }[]
      // TEXT: text: string
      // FILE_UPLOAD: file_name: string, comment: string
    }
  },
  started_at: ISO_timestamp,
  last_saved_to_local_storage: ISO_timestamp
}
```

### Edit Mode State

```
edit_state = {
  test_id: string,
  current_question_id: string,
  questions: Question[],           // loaded from server
  pending_patch: Partial<Question> | null,  // debounced changes
  last_synced_at: ISO_timestamp,
  save_status: "idle" | "saving" | "saved" | "error"
}
```

### Review Mode State

```
review_state = {
  attempt_id: string,
  attempt: Attempt,                 // includes score, max_score, time_spent
  questions: QuestionWithResult[],  // includes user_answer, correct_answer, points_earned, is_correct
  current_question_index: number
}
```

```
QuestionWithResult = Question & {
  user_answer: AnswerValue,
  correct_answer: AnswerValue,
  points_earned: number,
  is_correct: boolean | null       // null for ungraded (e.g., file upload pending review)
}
```

---

## 16. Backend Interaction Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tests/:testId/questions` | GET | Load all questions for a test |
| `/tests/:testId/questions` | POST | Create new empty question (edit mode) |
| `/tests/:testId/questions/:questionId` | PATCH | Update question (auto-save, typst save) |
| `/tests/:testId/questions/:questionId` | DELETE | Delete question (edit mode) |
| `/tests/:testId/questions/:questionId/typst` | PATCH | Update Typst source (same as question PATCH) |
| `/tests/:testId/questions/:questionId/media` | POST | Upload media file |
| `/tests/:testId/questions/:questionId/media/:mediaId` | DELETE | Remove media file |
| `/tests/:testId/attempts` | POST | Start new attempt (take mode) |
| `/attempts/:attemptId` | GET | Get attempt with answers for review |
| `/attempts/:attemptId/submit` | POST | Finalize attempt, clear local cache |

---

End of document.
