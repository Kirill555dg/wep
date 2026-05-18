# ISLAND-2: Auth Pages (Login / Register)

## Goal

Update existing login (`/login`) and register (`/register`) pages to use the new
API client and match the minimal design of the rest of the app.

## Current state

Login and register pages **already exist and are functional**:
- `src/pages/login/LoginPage.tsx` — works, uses old manual API
- `src/pages/register/RegisterPage.tsx` — works, uses old manual API
- `src/features/auth/api/useAuth.ts` — already migrated to new `@hey-api` client

What’s needed:
1. Refactor the pages to use **react-hook-form + Zod** (currently manual state)
2. Remove styled gradients and heavy visual elements — keep minimal
3. Ensure error handling uses API error envelope format

## Design reference

`docs/dev/frontend/03-auth.md`

Visual: centered card, minimal, airy.

```
┌──────────────────────────────────────┐
│         📐 WEP (small logo)            │
│                                      │
│         Welcome back                 │
│                                      │
│  Email or username                   │
│  ┌────────────────────────┐         │
│  │                        │         │
│  └────────────────────────┘         │
│                                      │
│  Password                            │
│  ┌────────────────────────┐         │
│  │                        │         │
│  └────────────────────────┘         │
│                                      │
│  [ Sign In ]                         │
│                                      │
│  Don't have an account? Register     │
└──────────────────────────────────────┘
```

## Files to modify

| File | Action |
|---|---|
| `src/pages/login/LoginPage.tsx` | Refactor to react-hook-form + Zod, simplify UI |
| `src/pages/register/RegisterPage.tsx` | Refactor to react-hook-form + Zod, simplify UI |

## Component architecture

Both pages share a common `AuthCard` wrapper:

```
AuthCard
├── Logo (→ /catalog)
├── Title
├── Form (react-hook-form + zod)
│   ├── InputField (email/username)
│   ├── InputField (password)
│   └── SubmitButton
└── AltLink (Login ↔ Register)
```

### Validation schemas

```ts
// login
const loginSchema = z.object({
  username_or_email: z.string().min(1, 'Введите email или логин'),
  password: z.string().min(8, 'Минимум 8 символов'),
})

// register
const registerSchema = z.object({
  first_name: z.string().min(1, 'Обязательное поле'),
  last_name: z.string().min(1, 'Обязательное поле'),
  username: z.string().min(3, 'Минимум 3 символа'),
  email: z.string().email('Неверный email'),
  password: z.string().min(8, 'Минимум 8 символов'),
})
```

### API usage

```tsx
import { useMutation } from '@tanstack/react-query'
import { loginApiV1AuthLoginPost, registerApiV1AuthRegisterPost } from '@/shared/api'
import { client } from '@/shared/api/generated/client.gen'

const login = useMutation({
  mutationFn: (body: LoginRequest) => loginApiV1AuthLoginPost({ client, body }),
  onSuccess: (res) => {
    // res.data has { access_token, token_type, user }
    useUserStore.getState().setToken(res.data.access_token)
    useUserStore.getState().setUser(res.data.user)
    navigate('/catalog')
  },
})
```

**Important**: do NOT call `getCurrentUserProfileApiV1AuthMeGet` after login. The login response already includes the `user` object.

### Error display

API errors come in the format:
```json
{ "error": { "code": "invalid_credentials", "message": "..." } }
```

Extract with `getApiError(err)` from `@/shared/lib/api-error.ts`.

Show errors:
- As a toast (`react-hot-toast`) for generic errors
- Under the specific field (if validation error from Zod)

### Redirect after auth

- After login/register → `/catalog`
- If user was redirected (`/login?redirect=/history`), go to that page instead of catalog

### Guest gating

If user visits `/login` while already authenticated, redirect to `/catalog`.

## Verification checklist

- [ ] Build passes
- [ ] Both pages use `react-hook-form` + Zod
- [ ] Login works (POST /api/v1/auth/login) and redirects to catalog
- [ ] Register works (POST /api/v1/auth/register) and redirects to catalog
- [ ] Error from API shown in form or as toast
- [ ] Links between pages work (Login → Register and vice versa)
- [ ] Already-authenticated users are redirected away from auth pages
- [ ] `?redirect=` query param honored after login

## Design file

`docs/dev/frontend/03-auth.md`
