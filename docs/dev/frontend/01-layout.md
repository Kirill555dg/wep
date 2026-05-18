# Layout

Общий каркас страниц. Никакого стандартного хедера/футера — только минимальная верхняя панель.

## Размеры

```
┌──────────────────────────────────────────────────────────────┐
│  h-12 (48px) — Top bar    w-full    z-50  bg-white/80        │
│  backdrop-blur  border-b                                   │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  Content area  —  min-h-screen  —  pt-6  px-8  pb-12       │
│                                                              │
│                                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## Top bar (без авторизации)

```
┌──────────────────────────────────────────────────────────────┐
│  📐 WEP                                        [Login]      │
│  ^--- logo / brand, ссылка на /catalog                      │
│                                               link to /login│
└──────────────────────────────────────────────────────────────┘
```

### Элементы

| Элемент | Поведение |
|---|---|
| WEP logo | Click → `/catalog` |
| Login | Click → `/login`. Показывать только если `!token` |

## Top bar (с авторизацией)

```
┌──────────────────────────────────────────────────────────────┐
│  📐 WEP    [My Tests]  [History]           [👤 John ▼]     │
│  ^--- logo    link        link                dropdown menu │
└──────────────────────────────────────────────────────────────┘
```

### Nav элементы

| Элемент | Роут | Активный when |
|---|---|---|
| WEP | `/catalog` | path === `/catalog` |
| My Tests | `/my-tests` | path.startsWith(`/my-tests`) |
| History | `/history` | path.startsWith(`/history`) |

### User dropdown (навигация)

При клике на аватар/имя — выпадающее меню:

```
┌──────────────────┐
│  Profile          │ → /profile
│  ────────────    │
│  Settings         │ → /settings (будущее)
│  ────────────    │
│  Sign out         │ → logout → /catalog
└──────────────────┘
```

## Content area

- `max-w-7xl mx-auto` для страниц-списков (catalog, my-tests, history)
- `max-w-4xl mx-auto` для форм (settings, profile)
- `w-full` для take/edit (на всю ширину)

## Компоненты

### `TopBar`

```
TopBar
├── Logo (/catalog)
├── NavLinks (conditional on auth)
│   ├── MyTestsLink
│   └── HistoryLink
└── UserSection
    ├── LoginButton (if !token)
    └── UserMenu (if token)
        └── Avatar + dropdown
```

### Mobile

На мобильных (≤768px) навигация прячется в `hamburger`:

```
┌──────────────────────────────────┐
│  📐 WEP                    ☰ 👤 │
├──────────────────────────────────┤
│  (hamburger menu overlay)       │
│  ────────────────────────────  │
│  Catalog                        │
│  My Tests                       │
│  History                        │
│  Profile                        │
│  Sign out                       │
└──────────────────────────────────┘
```

## Page wrapper

Каждая страница — `Page`-компонент, который использует `TopBar`:

```tsx
<Page>
  <TopBar />
  <main>{children}</main>
</Page>
```
