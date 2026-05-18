# Profile — `/profile`

Редактирование личной информации и аватар. **Никакой статистики** — вся статистика в History.

## Layout

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│  Profile                                                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │                         ┌────────┐                │     │
│  │                         │  🧑    │                │     │
│  │                         │ [Edit] │                │     │
│  │                         └────────┘                │     │
│  │                                                    │     │
│  │  John Doe                                          │     │
│  │  john.doe@example.com                              │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Personal Information                              │     │
│  │  ───────────────────────────                       │     │
│  │                                                    │     │
│  │  First Name                                        │     │
│  │  ┌────────────────────────────────────────────┐   │     │
│  │  │ John                                        │   │     │
│  │  └────────────────────────────────────────────┘   │     │
│  │                                                    │     │
│  │  Last Name                                         │     │
│  │  ┌────────────────────────────────────────────┐   │     │
│  │  │ Doe                                         │   │     │
│  │  └────────────────────────────────────────────┘   │     │
│  │                                                    │     │
│  │  Middle Name (optional)                            │     │
│  │  ┌────────────────────────────────────────────┐   │     │
│  │  │                                            │   │     │
│  │  └────────────────────────────────────────────┘   │     │
│  │                                                    │     │
│  │  Username                                         │     │
│  │  ┌────────────────────────────────────────────┐   │     │
│  │  │ johndoe                                     │   │     │
│  │  └────────────────────────────────────────────┘   │     │
│  │                                                    │     │
│  │  Email                                            │     │
│  │  ┌────────────────────────────────────────────┐   │     │
│  │  │ john@example.com                           │   │     │
│  │  └────────────────────────────────────────────┘   │     │
│  │                                                    │     │
│  │  [Save Changes]                                    │     │
│  └────────────────────────────────────────────────────┘     │
└──────────────────────────────────────────────────────────────┘
```

## Avatar section

```
┌────────┐
│  🧑    │ h-24 w-24 rounded-full
│ [Edit] │
└────────┘
```

| Элемент | Поведение |
|---|---|
| Avatar | Current avatar or fallback initials |
| [Edit] | Click → file picker (image/*) → upload to MinIO → update preview |

## Form fields

| Field | Type | Validation |
|---|---|---|
| First Name | `input type="text"` | Required, max 100 |
| Last Name | `input type="text"` | Required, max 100 |
| Middle Name | `input type="text"` | Optional |
| Username | `input type="text"` | Required, unique |
| Email | `input type="email"` | Required, valid |

## Actions

| Действие | Триггер | Результат |
|---|---|---|
| Save | Click [Save Changes] | PATCH `/users/me` → toast "Saved" |
| Edit avatar | Click [Edit] on avatar | File picker → upload → update |
| Cancel | Click "←" or navigate away | No changes saved |

## States

| State | Визуал |
|---|---|
| Loading | Form skeleton |
| Saving | Button disabled + spinner |
| Saved | Toast "Profile updated" |
| Error (avatar) | Toast "Upload failed, max 5MB" |
| Error (form) | Field validation errors |
