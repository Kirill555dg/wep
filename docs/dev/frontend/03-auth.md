# Auth — `/login` / `/register`

## Login `/login`

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar (only Logo, no Login btn)                          │
│──────────────────────────────────────────────────────────────│
│                                                              │
│                                                              │
│                     ┌──────────────────┐                    │
│                     │  Welcome back    │                    │
│                     │                  │                    │
│                     │  Email or        │                    │
│                     │  Username        │                    │
│                     │  ┌──────────┐   │                    │
│                     │  │          │   │                    │
│                     │  └──────────┘   │                    │
│                     │                  │                    │
│                     │  Password        │                    │
│                     │  ┌──────────┐   │                    │
│                     │  │          │   │                    │
│                     │  └──────────┘   │                    │
│                     │                  │                    │
│                     │  [Sign In]       │                    │
│                     │                  │                    │
│                     │  Don't have an   │                    │
│                     │  account?        │                    │
│                     │  Register        │                    │
│                     └──────────────────┘                    │
│                                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Card

- `w-[400px]` card centered (`mx-auto mt-[15vh]`)
- Card header: "Welcome back"
- Card content: form fields
- Card footer: register link

### Form fields

| Field | Type | Validation |
|---|---|---|
| username_or_email | `input type="text"` | Required |
| password | `input type="password"` | Required |

### Actions

| Действие | Триггер | Результат |
|---|---|---|
| Sign In | Click btn or Enter | POST `/api/v1/auth/login` → save token → redirect `/catalog` |
| Go to Register | Click "Register" | Navigate `/register` |

### States

| State | Визуал | Поведение |
|---|---|---|
| Default | Empty form | — |
| Submitting | Button disabled + spinner | Поля disabled |
| Error | Error message below form | Тосты `react-hot-toast` — "Invalid credentials" |
| Success | — | Redirect `/catalog` |

---

## Register `/register`

```
┌──────────────────────────────────────────────────────────────┐
│  Top bar                                                     │
│──────────────────────────────────────────────────────────────│
│                                                              │
│                     ┌────────────────────────┐              │
│                     │  Create an account     │              │
│                     │                        │              │
│                     │  First Name            │              │
│                     │  ┌────────────────┐   │              │
│                     │  │                │   │              │
│                     │  └────────────────┘   │              │
│                     │                        │              │
│                     │  Last Name             │              │
│                     │  ┌────────────────┐   │              │
│                     │  │                │   │              │
│                     │  └────────────────┘   │              │
│                     │                        │              │
│                     │  Email                 │              │
│                     │  ┌────────────────┐   │              │
│                     │  │                │   │              │
│                     │  └────────────────┘   │              │
│                     │                        │              │
│                     │  Username              │              │
│                     │  ┌────────────────┐   │              │
│                     │  │                │   │              │
│                     │  └────────────────┘   │              │
│                     │                        │              │
│                     │  Password              │              │
│                     │  ┌────────────────┐   │              │
│                     │  │                │   │              │
│                     │  └────────────────┘   │              │
│                     │                        │              │
│                     │  [Create Account]      │              │
│                     │                        │              │
│                     │  Already registered?   │              │
│                     │  Sign In               │              │
│                     └────────────────────────┘              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Card

- `w-[450px]` card centered
- Same layout pattern as login

### Form fields

| Field | Type | Validation |
|---|---|---|
| first_name | text | Required, max 100 |
| last_name | text | Required, max 100 |
| email | email | Required, valid email |
| username | text | Required, max 100 |
| password | password | Required, min 8 |

### Actions

| Действие | Триггер | Результат |
|---|---|---|
| Create Account | Click btn or Enter | POST `/api/v1/auth/register` → auto-login → redirect `/catalog` |
| Go to Login | Click "Sign In" | Navigate `/login` |

### States

| State | Визуал |
|---|---|
| Default | Empty form |
| Field error | Red border + error text under field |
| Submitting | Button disabled + spinner |
| Success | — → redirect `/catalog` |

## Redirect logic

- If user hits `/login` or `/register` **and** is already authenticated (`token` exists): redirect to `/catalog`
- If user hits any auth-required page **without** token: redirect to `/login?redirect=...`, after login redirect back
