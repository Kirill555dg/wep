# Frontend - руководство разработчика

Детальное руководство по разработке клиентской части WEP.

## Требования

- Node.js >= 18.x (рекомендуется LTS)
- npm или pnpm

## Установка окружения

### Node.js

#### macOS (Homebrew):
```bash
brew install node
```

#### macOS/Linux (nvm - рекомендуется):
```bash
# Установка nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Перезапуск терминала
source ~/.zshrc  # для zsh
source ~/.bashrc # для bash

# Установка Node.js LTS
nvm install --lts
nvm use --lts
```

#### Проверка:
```bash
node --version  # >= 18.x
npm --version
```

## Установка проекта

```bash
cd frontend

# Установка зависимостей
npm install

# Настройка окружения
cp .env.example .env
# Отредактировать VITE_API_URL
```

## Запуск

### Development
```bash
npm run dev
```
http://localhost:5173

### Production build
```bash
npm run build
npm run preview
```

## Тестирование

### Unit-тесты (Vitest)
```bash
# Один раз
npm test

# Watch режим
npm run test:watch
```

### E2E-тесты (Cypress)
```bash
# Запуск тестов
npm run test:e2e

# Cypress UI
npm run cypress
```

## Структура проекта (FSD)

```
src/
├── app/               # Инициализация приложения
│   ├── index.tsx      # Главный компонент
│   ├── providers/     # Провайдеры (Auth, Query)
│   └── router/        # Роутинг, guards
│
├── pages/             # Страницы приложения
│   ├── auth/          # Авторизация
│   ├── profile/       # Профиль
│   ├── student/       # Страница студента
│   ├── teacher/       # Страница преподавателя
│   └── notifications/ # Уведомления
│
├── widgets/           # Композитные UI-блоки
│   ├── header/        # Шапка
│   ├── footer/        # Подвал
│   └── layout/        # Layout
│
├── features/          # Бизнес-функции
│   ├── auth/          # Авторизация
│   ├── profile/       # Профиль
│   ├── notifications/ # Уведомления
│   └── join-class/    # Присоединение к классу
│
├── entities/          # Бизнес-сущности
│   ├── user/          # Пользователь
│   ├── student/       # Студент
│   ├── teacher/       # Преподаватель
│   ├── class/         # Класс
│   └── notification/  # Уведомление
│
└── shared/            # Переиспользуемый код
    ├── ui/            # UI-компоненты
    ├── hooks/         # Общие хуки
    ├── lib/           # Утилиты
    ├── api/           # API клиент
    ├── styles/        # Глобальные стили
    └── assets/        # Иконки, изображения
```

## Слои FSD

1. **app** - инициализация, провайдеры, роутинг
2. **pages** - страницы приложения
3. **widgets** - композитные блоки UI
4. **features** - части бизнес-логики
5. **entities** - бизнес-сущности
6. **shared** - переиспользуемый код

**Правило зависимостей**: верхние слои зависят от нижних, но не наоборот.

## Path Aliases

Настроены алиасы для удобного импорта:

```typescript
import { Button } from "@/shared/ui/button";
import { useAuth } from "@/features/auth/model/store";
import { UserAvatar } from "@/entities/user/ui/UserAvatar";
```

## Добавление новой фичи

1. Создайте папку `src/features/feature-name/`
2. Добавьте слои:
   - `api/` - API запросы
   - `model/` - store, типы
   - `ui/` - компоненты
   - `lib/` - утилиты
3. Подключите в нужной странице

**Пример структуры**:
```
features/homework-player/
├── api/
│   └── queries.ts        # React Query hooks
├── model/
│   ├── types.ts          # TypeScript типы
│   └── store.ts          # Zustand store
├── ui/
│   ├── HomeworkPlayer.tsx
│   └── ProblemCard.tsx
└── lib/
    └── draft.ts          # Утилиты работы с черновиками
```

## Добавление новой сущности

1. Создайте папку `src/entities/entity-name/`
2. Определите типы в `model/types.ts`
3. Создайте API слой в `api/`:
   - `queryKeys.ts` - ключи React Query
   - `queries.ts` - React Query hooks
4. Добавьте UI-компоненты в `ui/`

**Пример**:
```
entities/homework/
├── api/
│   ├── queryKeys.ts
│   └── queries.ts
├── model/
│   └── types.ts
└── ui/
    └── HomeworkCard.tsx
```

## Добавление новой страницы

1. Создайте папку `src/pages/page-name/`
2. Добавьте главный компонент `PageName.tsx`
3. Создайте UI-компоненты в `ui/`
4. Добавьте маршрут в `src/app/index.tsx`

**Пример**:
```typescript
// src/app/index.tsx
{
  path: '/teacher/homework/:id',
  element: <RequireAuth><RequireRole role="teacher">
    <TeacherHomeworkPage />
  </RequireRole></RequireAuth>
}
```

## Работа с API

### React Query

Все запросы к API через React Query:

```typescript
// entities/classroom/api/queries.ts
export const useClassrooms = () => {
  return useQuery({
    queryKey: classroomKeys.all,
    queryFn: () => classroomsApi.list()
  });
};

// Использование
const { data, isLoading } = useClassrooms();
```

### Мутации

```typescript
const mutation = useMutation({
  mutationFn: (data) => homeworkApi.submit(data),
  onSuccess: () => {
    queryClient.invalidateQueries(homeworkKeys.all);
    toast.success('Отправлено');
  }
});
```

## Работа с формами

React Hook Form + Zod:

```typescript
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

const form = useForm({
  resolver: zodResolver(schema)
});
```

## Стилизация

### TailwindCSS

Используйте utility-классы:

```tsx
<div className="flex items-center gap-4 p-4 rounded-lg bg-card">
  <Button variant="primary" size="lg">
    Сохранить
  </Button>
</div>
```

### UI-компоненты (Radix UI)

Базовые компоненты в `shared/ui/`:
- Button, Input, Card
- Dialog, Dropdown, Toast
- Avatar, Badge, Label

### Кастомизация

Цвета и темы настраиваются в:
- `tailwind.config.ts` - TailwindCSS конфигурация
- `src/shared/styles/globals.css` - CSS переменные

## Соглашения

### Именование файлов

- Компоненты: `PascalCase.tsx` (UserAvatar.tsx)
- Утилиты: `camelCase.ts` (formatDate.ts)
- Хуки: `use*.ts` (useAuth.ts)
- Типы: `types.ts` или `*.types.ts`

### Именование компонентов

```typescript
// Экспорт по умолчанию для страниц
export default function LoginPage() {}

// Именованный экспорт для компонентов
export const UserAvatar = () => {}
```

### TypeScript

- Strict mode включен
- Избегайте `any`
- Используйте type inference где возможно
- Определяйте Props интерфейсы

```typescript
interface UserAvatarProps {
  userId: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const UserAvatar = ({ userId, size = 'md', className }: UserAvatarProps) => {
  // ...
};
```

## Частые команды

```bash
# Разработка
npm run dev

# Сборка
npm run build
npm run preview

# Тесты
npm test
npm run test:watch
npm run test:e2e

# Проверка типов
npm run typecheck
```

## Отладка

### React DevTools

Установите расширение React DevTools для Chrome/Firefox.

### Redux DevTools

Для отладки Zustand store включите Redux DevTools middleware.

### Network

Используйте вкладку Network в DevTools для проверки API запросов.

## Полезные ссылки

- [Feature-Sliced Design](https://feature-sliced.design/)
- [React Query](https://tanstack.com/query/latest)
- [React Hook Form](https://react-hook-form.com/)
- [TailwindCSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
