# ISLAND-1: Catalog Page

## Goal

Build the **catalog page** (`/catalog`) — the main page users land on. It lists public
tests in a responsive grid card layout with search and tag filtering.

## Design reference

Full visual specification in `docs/dev/frontend/02-catalog.md`.

Key visual points:
- Top bar already present (48px sticky, handled by `TopBar.tsx`)
- Search bar centered with debounced input
- Tag filter chips in a horizontal scrollable row
- Test cards in a responsive grid: 1 col mobile → 2 md → 4 xl
- Each card: cover image (optional), title, tag chips, author name
- Empty state when no tests match filters

## Files to modify

| File | Action |
|---|---|
| `src/pages/catalog/CatalogPage.tsx` | Replace placeholder with full implementation |
| `src/pages/catalog/CatalogPage.css` | Do NOT create — only Tailwind |

## Component architecture

```
CatalogPage
├── SearchBar           (controlled input, debounced 300ms)
│   └── useQueryString  (syncs URL ?q=...)
├── TagFilter           (horizontal scroll chips)
│   └── useTagsQuery    (GET /api/v1/tags)
└── TestGrid            (responsive grid)
    ├── TestCard        (for each result)
    │   ├── Image/Placeholder
    │   ├── TitleLink     (→ `/tests/${id}`)
    │   ├── TagChips
    │   └── MetaRow       (author · questions · duration)
    └── EmptyState (if 0 results)
```

### Component details

#### SearchBar

```tsx
const [q, setQ] = useState(searchParams.get('q') || '')
useDebounce(() => setSearchParams({ q }), 300, [q])
```

- Placeholder: `Поиск тестов...`
- `type="search"`
- Debounce 300ms, sync to `URLSearchParams`

#### TagFilter

```tsx
const { data: tags } = useQuery({
  queryKey: ['tags'],
  queryFn: () => listTagsApiV1TagsGet({ client }),
})
```

- Horizontal scroll row: `<div className="flex gap-2 overflow-x-auto pb-1">`
- Tag chip: `<Badge variant={active ? 'default' : 'outline'}>{tag.name}</Badge>`
- Click toggles selection of tag slug
  - `onClick` → update search params: `?q=math&tags=math,algebra`
- First chip is `All` ( resets selection when clicked )

#### TestCard

```tsx
interface TestCardProps {
  test: TestResponse
  onTagClick: (slug: string) => void
}
```

Layout:
```
┌──────────────────────────┐
│  🖼 Cover (h-48 object-cover) │
│                          │
├──────────────────────────┤
│  Title                   │
│  [tag] [tag]             │
│  Author · 15 qns · 30min │
└──────────────────────────┘
```

Styling:
- Card hover: `group hover:-translate-y-0.5 hover:shadow-md transition-all`
- Cover fallback (if no `image_url`): gradient `bg-gradient-to-br from-indigo-100 to-blue-50`
- Tags: clickable `Badge`; clicking filters catalog by that tag
- Author: clickable `span`; clicking filters catalog by author
  - Actually author is clickable → filter by `authorId` (GET param)

### Data fetching

```tsx
const q = searchParams.get('q') || ''
const tags = searchParams.get('tags')?.split(',').filter(Boolean) || []

const { data, isLoading, error } = useQuery({
  queryKey: ['catalog', q, tags.join(',')],
  queryFn: () => searchCatalogApiV1CatalogGet({
    client,
    query: {
      q: q || undefined,
      tags: tags.length > 0 ? tags : undefined,
      skip: 0,
      limit: 20,
    } as any, // SDK uses query types.
  }),
})
```

**Note:** `searchCatalogApiV1CatalogGet` already supports `q`, `tags[]`, `skip`, `limit`.

The schema `CatalogSearchParams` is in `types.gen.ts`:
```ts
interface CatalogSearchParams {
  q?: string | null
  tags: string[]
  skip: number
  limit: number
}
```

For tags, the backend expects them as comma-separated or repeated params depending on SDK generation. If the SDK requires `tags` as string, pass as comma-separated.

### States

| State | UI |
|---|---|
| Loading | Skeleton grid (4-6 shimmering card placeholders) |
| Empty (no results) | "Нет тестов по заданному запросу" + clear filters button |
| Error | Toast + `[Retry]` button |
| Success | Grid of `TestCard` |

### Empty state

```tsx
if (data?.length === 0) {
  return (
    <div className="text-center py-16">
      <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <p className="text-gray-500">Нет тестов по заданному запросу</p>
      <Button variant="ghost" onClick={() => { setQ(''); setTags([]); }}>
        Сбросить фильтры
      </Button>
    </div>
  )
}
```

### Navigation from card

Clicking a card body navigates to `/tests/${test.id}` (test view page).
Clicking a tag chip inside the card changes the catalog filter.
Clicking an author name also changes catalog filter by author.

### URL sync

- `?q=math` — search text
- `?tags=math,algebra` — selected tags
- `?authorId=5` — when filtering by author

Use `useSearchParams()` from `react-router-dom`.

## Verification checklist

- [ ] Page renders without errors (`npx vite build` passes)
- [ ] Search updates URL `?q=` after 300ms debounce
- [ ] Tag chips are fetched from backend and clickable
- [ ] Card grid is responsive (1/2/4 cols)
- [ ] Empty state shown when no results
- [ ] Card click navigates to `/tests/:id`
- [ ] Tag click filters catalog by that tag
- [ ] Author click filters catalog by author (via `authorId` query param)
- [ ] Loading skeleton shown while fetching

## Backend dependencies (already done)

- `GET /api/v1/catalog` — `searchCatalogApiV1CatalogGet`
- `GET /api/v1/catalog/:id` — `getPublicTestApiV1CatalogTestIdGet`
- `GET /api/v1/tags` — `listTagsApiV1TagsGet`
- `GET /api/v1/catalog/?author_id=X` — filter by author (added in backend deps)

## Design file

`docs/dev/frontend/02-catalog.md` — wireframes, card specs, filter behavior.
