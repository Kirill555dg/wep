# ISLAND-7: My Tests Page (`/my-tests`)

## Goal

Build the **"My Tests" page** — lists tests created by the current user.
Uses the **same card grid** as the catalog but with author controls.

## Design reference

`docs/dev/frontend/08-my-tests.md`

## Files to modify

| File | Action |
|---|---|
| `src/pages/my-tests/MyTestsPage.tsx` | Replace placeholder |

## Component architecture

```
MyTestsPage
├── PageHeader
│   ├── "My Tests" title
│   └── [+ New Test] button → POST /tests → redirect to edit
├── FilterTabs
│   ├── [All] [Published] [Private]
│   └── Same tag chips as catalog
└── TestGrid (same grid as catalog)
    ├── TestCard (same component as catalog)
    │   ├── Cover image
    │   ├── Title
    │   ├── Tags
    │   ├── Visibility badge (🟢 Published / 🔒 Private)
    │   ├── Attempt count / average score
    │   └── Date
    └── CardActions (overlay or bottom)
        ├── [Edit questions] → /tests/:id/edit
        ├── [Settings] → /tests/:id/settings
        └── 🗑 Delete → confirm dialog → DELETE
```

### Data

```tsx
const { data: tests } = useQuery({
  queryKey: ['my-tests'],
  queryFn: () => listMyTestsApiV1TestsGet({ client }),
})
```

`listMyTestsApiV1TestsGet` returns `TestResponse[]` (with `is_public`, `questions_count`, etc.)

**Question count accuracy:** Backend `questions_count` is automatically maintained (or should be re-verified after question edits).

### [+ New Test] button

```tsx
const navigate = useNavigate()
const create = useMutation({
  mutationFn: () => createTestApiV1TestsPost({
    client,
    body: {
      title: '',
      is_public: false,
      attempt_limit: null,
      tag_names: [],
    },
  }),
  onSuccess: (res) => navigate(`/tests/${res.data.id}/edit`),
})
```

Default new test: empty title, private, unlimited attempts, empty tags.
Posts then immediately opens in edit mode.

### Filter tabs

State: `filter: 'all' | 'published' | 'private'`
Just client-side filter the list for now (tests arrays are expected to be small);
if pagination needed later, add query params.

### Verification checklist

- [ ] Build passes
- [ ] Requires auth
- [ ] Fetches user's tests
- [ ] Filter tabs work
- [ ] Card grid uses same component as catalog
- [ ] [+ New Test] creates a new test and redirects to edit
- [ ] Edit links work
- [ ] Settings links work
- [ ] Delete with confirmation

## Related islands

- **ISLAND-1 (Catalog)** — same card component
- **ISLAND-4 (Test Content)** — edit link goes here
- **ISLAND-? (Test Settings)** — settings link goes here

## Design file

`docs/dev/frontend/08-my-tests.md`
