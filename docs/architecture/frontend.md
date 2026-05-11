# Frontend архитектура

Детальное описание архитектуры клиентской части WEP.

## Назначение frontend

Frontend - клиентский компонент LMS, который:

- Реализует UI/UX и пользовательские сценарии (teacher/student)
- Обеспечивает навигацию и роль-ориентированные ограничения
- Управляет клиентским состоянием и кэшированием данных
- Визуализирует статистику
- Интегрируется с backend через типизированный API-контракт

## Feature-Sliced Design

Зависимости направлены вниз (от верхних слоев к нижним):

```
app/          ← bootstrap, routing, guards
  ↓
pages/        ← route screens
  ↓
widgets/      ← composite UI blocks
  ↓
features/     ← user scenarios
  ↓
entities/     ← domain data (queries)
  ↓
shared/       ← ui-kit, api, utils
```

## Слои FSD

### `shared/` - инфраструктура и UI-kit

**Назначение**: Переиспользуемые компоненты без знания предметной области

**Компоненты**:

- `shared/ui/*` - дизайн-система (Button, Card, Form, Dialog, Toast, etc.)
- `shared/api/*` - API интеграция:
  - `generated/*` - OpenAPI-generated клиент
  - `openapi.ts` - конфигурация клиента
  - `auth.ts`, `classrooms.ts`, etc. - wrappers
  - `errors.ts` - обработка ошибок
  - `pagination.ts` - пагинация
- `shared/config/*` - env, routes
- `shared/lib/*` - утилиты (logger, formatters, cn)
- `shared/hooks/*` - общие хуки (useMediaQuery, useToast)

**Правило**: Не зависит от других слоёв FSD

### `entities/` - доменные сущности

**Назначение**: Инкапсулировать работу с доменными сущностями

**Компоненты**:

- `entities/*/api/queryKeys.ts` - ключи кэша React Query
- `entities/*/api/queries.ts` - React Query hooks
- `entities/session/*` - session store (user/role/token)

**Примеры**:
- `entities/classroom` - классы
- `entities/lesson` - уроки
- `entities/homework` - домашние задания
- `entities/statistics` - статистика
- `entities/chat` - чат

**Правило**: Может зависеть только от `shared/`

### `features/` - пользовательские действия

**Назначение**: Оформить действие пользователя как модуль

**Примеры**:
- `features/homework/player` - выполнение ДЗ (stepper, drafts)
- `features/auth/login` - форма входа
- `features/classroom/join` - присоединение к классу

**Компоненты**:
- Сценарный UI
- Локальное состояние
- Обработка ошибок UX-уровня

**Правило**: Может зависеть от `entities/*` и `shared/`

### `widgets/` - композитные блоки

**Назначение**: Большие UI-блоки для страниц

**Примеры**:
- `widgets/layout/*` - каркас приложения (shell)
- `widgets/navigation/*` - sidebar, mobile nav
- `widgets/chat/*` - realtime чат (WS + fallback)
- `widgets/statistics/*` - графики/таблицы

**Правило**: Может зависеть от `features/*`, `entities/*`, `shared/`

### `pages/` - маршрутизируемые экраны

**Назначение**: Конечные страницы (URL → Page)

**Структура**:
- `pages/teacher/*` - страницы преподавателя
- `pages/student/*` - страницы студента
- `pages/chat/*` - чат
- `pages/auth/*` - аутентификация

**Логика**:
- Orchestration: извлечь `:id` из URL, выбрать виджет
- Не содержит бизнес-логику данных

**Правило**: Может зависеть от всех нижних слоёв

### `app/` - точка сборки

**Назначение**: Верхний слой, bootstrap приложения

**Компоненты**:
- `app/index.tsx` - роутинг
- `app/router/guards.tsx` - RequireAuth, RequireRole
- `app/providers/*` - React Query provider, session bootstrap

**Правило**: Может зависеть от всех слоёв

## API интеграция

### Типизированный клиент

```
Backend (FastAPI)
  → export OpenAPI JSON
    → openapi-typescript-codegen
      → shared/api/generated/*
```

### React Query

- Кэширование запросов
- Автоматическая ре-фетч стратегия
- Optimistic updates
- Инвалидация кэша

**Пример**:
```typescript
// entities/classroom/api/queries.ts
export const useClassrooms = () => {
  return useQuery({
    queryKey: classroomKeys.all,
    queryFn: () => classroomsApi.list()
  });
};
```

### Error handling

```typescript
// shared/api/errors.ts
export const handleApiError = (error: unknown) => {
  if (isApiError(error)) {
    const { code, message, request_id } = error.error;
    toast.error(message, { description: `ID: ${request_id}` });
  }
};
```

## Состояние приложения

### Session State (Zustand)

```typescript
// entities/session/model/store.ts
type SessionState = {
  user: User | null;
  token: string | null;
  role: 'teacher' | 'student';
  setUser: (user: User) => void;
  logout: () => void;
};
```

### Server State (React Query)

- Все данные с сервера кэшируются через React Query
- Единые query keys в `entities/*/api/queryKeys.ts`

### Local State (React hooks)

- Component state: `useState`, `useReducer`
- Forms: `react-hook-form` + `zod`

## Роутинг

### Guards

```typescript
// app/router/guards.tsx
<RequireAuth>
  <RequireRole role="teacher">
    <TeacherHomePage />
  </RequireRole>
</RequireAuth>
```

### Routes

```typescript
// app/index.tsx
const router = createBrowserRouter([
  { path: '/login', element: <LoginPage /> },
  { 
    path: '/teacher',
    element: <RequireAuth><RequireRole role="teacher">...</RequireRole></RequireAuth>,
    children: [
      { path: '', element: <TeacherHomePage /> },
      { path: 'classrooms/:id', element: <TeacherClassroomPage /> },
      ...
    ]
  },
  ...
]);
```

## Realtime (WebSocket)

### Чат

```typescript
// widgets/chat/ClassroomChat.tsx
const ws = useWebSocket(`/api/v1/classrooms/${id}/chat/ws`, {
  onMessage: (message) => {
    queryClient.setQueryData(chatKeys.messages(id), (old) => [...old, message]);
  },
  onError: () => {
    // fallback to HTTP polling
  }
});
```

## Визуализация данных

### Графики (recharts)

- `widgets/statistics/ProgressChart.tsx`
- Используется для визуализации прогресса

### Таблицы (@tanstack/react-table)

- `widgets/statistics/StatisticsTable.tsx`
- Сортировка, фильтрация, пагинация

## Технологический стек

- **TypeScript** - типобезопасность
- **React 18** - UI библиотека
- **Vite** - сборщик
- **TailwindCSS** - стили
- **React Router** - маршрутизация
- **React Query** - data fetching
- **React Hook Form** - формы
- **Zod** - валидация
- **Zustand** - state management
- **Recharts** - графики
- **Radix UI** - headless компоненты

## Тестирование

- Unit tests: Vitest + Testing Library
- E2E tests: Cypress
- Coverage: Vitest coverage

## Доступность

- Semantic HTML
- ARIA attributes
- Keyboard navigation
- Screen reader support (Radix UI)
