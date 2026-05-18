# Frontend Developer Guide

## Технологический стек

- **React 18** + TypeScript
- **Vite** (build tool)
- **React Router v6**
- **@tanstack/react-query** (server state)
- **Zustand** + persist (client state)
- **Tailwind CSS** + shadcn/ui primitives
- **Typst.ts** (WASM renderer for math formulas)
- **Cypress** (E2E)
- **Vitest** (unit tests)

## Генерация API-клиента

Сервер экспортирует `/api/openapi.json`. Обновляйте SDK при изменении схемы:

```bash
cd frontend
bun generate-api   # openapi-ts
```

Сгенерированный код создаётся в `src/shared/api/generated/`. Эти файлы **не редактируются вручную**.

### Client Factory (`main.tsx`)

```ts
import { client } from '@/shared/api'

client.setConfig({
  auth: () => {
    const token = useUserStore.getState().token
    return token ?? undefined
  },
})
```

Все HTTP-вызовы через `client` автоматически получают Bearer-токен из Zustand store.

## FSD-архитектура

```
src/
├── app/          — роутинг, провайдеры, гварды
├── pages/        — страницы приложения
├── widgets/      — композитные UI-блоки (TopBar, QuestionPanel, …)
├── features/     — пользовательские сценарии (Auth, Render)
├── entities/     — доменные сущности (User, Attempt stores)
└── shared/       — ui-kit, api, utils, components
```

## Главные компоненты

| Путь | Назначение |
|---|---|
| `src/pages/test-content/TakeTestPage.tsx` | Единый take / edit / review |
| `src/pages/test-view/TestViewPage.tsx` | Страница теста (авторские инструменты, статистика) |
| `src/shared/components/AnswerBlocks.tsx` | Рендер ответов по типу (Single, Multiple, Text, File, Matching) |
| `src/shared/components/TypstRender.tsx` | WASM-рендер формул |

## Работа с состоянием

### Серверное (React Query)

```ts
const { data, isLoading } = useQuery({
  queryKey: ['active-attempt', testId],
  queryFn: () => getActiveAttemptApiV1AttemptsActiveGet({
    query: { test_id: testId }
  }),
})
```

Для мутаций (create / update / delete):
```ts
const mutation = useMutation({
  mutationFn: () => startAttemptApiV1AttemptsPost(
    { body: { test_id: id } }
  ),
  onSuccess: (res) => {
    if ((res as any).error) { toast.error(...) }
    else { navigate(`/tests/${testId}/take`) }
  },
})
```

### Клиентское (Zustand)

```ts
// entities/user/model/store.ts
import { useUserStore } from '@/entities/user/model/store'

useUserStore.getState().setToken(token)
useUserStore.getState().setUser(user)
```

> Парсер `persist middleware` сохраняет `user-store` в localStorage по дефолту.

## Cypress Injection

Для E2E в `main.tsx` экспортирована глобальная функция:

```ts
(window as any).__setAuth = (token, user) => {
  useUserStore.getState().setToken(token)
  useUserStore.getState().setUser(user)
}
```

Cypress `cy.loginAs('teacher')` делает API-login, потом вызывает `win.__setAuth(token, user)`.

## Типографика и формулы

В любой `text`/`textarea` поле Typst поддерживается:

```
$f'(x) = limit_(h->0) (f(x+h)-f(x))/h$
```

Рендеринг происходит через `<TypstRender source={...} />` или `TypstPreview` feature.

## Unit-тесты

```bash
bun test      # vitest run
bun test:watch # vitest watch mode
```

Конфигурация в `vitest.config.ts`. `jsdom` окружение, `globals: true`.

## Полезные alias-импорты (tsconfig paths)

| Alias | Путь |
|---|---|
| `@/app` | `src/app` |
| `@/pages` | `src/pages` |
| `@/widgets` | `src/widgets` |
| `@/features` | `src/features` |
| `@/entities` | `src/entities` |
| `@/shared` | `src/shared` |

## Чеклист при добавлении новой страницы

1. Добавить маршрут в `src/app/router.tsx`.
2. Если страница требует аутентификации, обернуть в `<AuthGuard>`.
3. Серверные данные — через `useQuery` с `queryKey`.
4. Мутации — через `useMutation` + `react-hot-toast` для ошибок.
5. Добавить Cypress spec с UUID-данными, если операция не идемпотентна.
