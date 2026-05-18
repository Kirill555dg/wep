# ISLAND-8: Profile Page (`/profile`)

## Goal

Update the **profile page** (`/profile`) to match the simplified design:
- Avatar edit
- Basic info editing
- No statistics (stats are in History)

## Design reference

`docs/dev/frontend/10-profile.md`

## Current state

Profile page exists (`src/pages/profile/ProfilePage.tsx`) but:
- Imports `useAuthorStats` from deleted `features/stats` (I already recreated the hook)
- Shows author stats inline (should NOT — stats go only to History)
- Uses manual form state (should use react-hook-form + Zod)
- Has old navigation links like /settings → remove

## Files to modify

| File | Action |
|---|---|
| `src/pages/profile/ProfilePage.tsx` | Refactor to match design |

## Component architecture

```
ProfilePage
├── AvatarSection
│   ├── Avatar (large, ~80px)
│   └── [Edit] overlay → file picker → upload → PATCH user avatar
├── ProfileForm
│   ├── react-hook-form + Zod
│   ├── First Name [____]
│   ├── Last Name [____]
│   ├── Middle Name (opt) [____]
│   ├── Username [____]
│   ├── Email [____]
│   └── [Save Changes]
└── LogoutButton
```

### Schema

```ts
const schema = z.object({
  first_name: z.string().min(1, 'Обязательное поле'),
  last_name: z.string().min(1, 'Обязательное поле'),
  middle_name: z.string().optional(),
  username: z.string().min(3, 'Минимум 3 символа'),
  email: z.string().email('Неверный email'),
})
```

### API

```tsx
const { mutate, isPending } = useMutation({
  mutationFn: (body: UserUpdate) => updateUserMeApiV1UsersMePatch({ client, body }),
  onSuccess: () => {
    toast.success('Профиль обновлён')
  },
})
```

**Note:** `updateUserMeApiV1UsersMePatch` may NOT exist yet in the generated SDK.
If missing, report it as a backend dependency rather than implementing a custom route.
The backend deps doc (`11-backend-deps.md`) lists it as needed.

For avatar upload:
```tsx
const upload = useMutation({
  mutationFn: (file: File) => uploadMediaApiV1MediaUploadPost({
    client,
    body: { file } as any
  }),
  onSuccess: (res) => {
    // PATCH user with avatar_url
  },
})
```

**Important:** if `POST /users/me/avatar` endpoint is missing from backend, note it in the island task and skip avatar upload until backend adds it.

### Remove these elements:

- Author stats section (remove entirely)
- /results link (history already lists results)
- /settings link (no settings page exists)

### Verification checklist

- [ ] Build passes
- [ ] Form uses react-hook-form + Zod
- [ ] All fields from UserUpdate schema editable
- [ ] Save calls PATCH API
- [ ] Logout works and redirects
- [ ] Avatar upload works (if backend supports) or shows "not yet available"

## Design file

`docs/dev/frontend/10-profile.md`
