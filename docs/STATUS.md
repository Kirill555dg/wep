# Текущее состояние проекта (Status)

**Updated:** 2026-05-18

## Infrastructure

| Сервис | Статус | Порт |
|---|---|---|
| PostgreSQL | Up (healthy) | 5433 |
| MinIO | Up (healthy) | 9000/9001 |
| Backend | Running with --reload | 8023 |
| Frontend dev | Running | 5173 |

## Seeded данные (налиты)

### Пользователи
- `teacher@wep.dev` / `TeacherPass123!` — автор 6 тестов
- `student@wep.dev` / `StudentPass123!` — 3 попытки

### Тесты (6 штук)
| ID | Название | Вопросы | Типы |
|---|---|---|---|
| 3 | Математика: Производные | 3 | SINGLE_CHOICE, TEXT |
| 4 | Физика: Механика | 2 | MULTIPLE_CHOICE, TEXT |
| 5 | Информатика: Алгоритмы | 1 | MATCHING |
| 6 | Английский: Аудирование | 1 | SINGLE_CHOICE |
| 7 | Химия: Органика | 1 | FILE_UPLOAD |
| 8 | Геометрия | 2 | SINGLE_CHOICE, ESSAY |

### Медиа в MinIO
- 5 изображений (BMP) — через POST /api/v1/media/upload
- 2 аудио (WAV) — через POST /api/v1/media/upload-answer
- 2 файла ответов (TXT, PDF) — через POST /api/v1/media/upload-answer

### Попытки
| Student | Тест | Статус | Score |
|---|---|---|---|
| student | Математика | completed | 4/4 |
| student | Химия | completed | 0/5 |
| student | Геометрия | in_progress | 1/2 |

## Backend changes

### Новые endpoints
- `GET /api/v1/tests/{test_id}/attempts` — таблица попыток для автора (paginated, с user_name)
- `GET /api/v1/tests/questions/pool` — вопросы автора для выбора из пула
- `POST /api/v1/tests/{test_id}/questions/{question_id}/from-pool` — копирование вопроса

### Схемы
- `AttemptAuthorSummary` — user_id, user_name, status, score, max_score, time_spent_minutes
- `PageAttemptAuthorSummary` — paginated wrapper
- `QuestionPoolResponse` — id, question_type, text, points, created_at

### Services
- `TestService.add_question_from_pool` — копирование options из исходного вопроса
- `AttemptRepository.list_by_test_with_users` — eager load User через selectinload
- `QuestionRepository.list_by_author_pool` — фильтрация по author_id + поиск по тексту

### Медиа
- `media_service.py` — добавлены типы: image/bmp, audio/x-wav, audio/m4a, video/avi
- `public_url()` — постоянные URLs без presigned (public-read bucket)

### Логирование
- `RotatingFileHandler` → `backend/logs/app.log` (10MB × 5 файлов)
- Формат JSON с `request_id`, `method`, `path`, `status_code`, `duration_ms`

### Исправления
- `AttemptStatus`, `QuestionType` добавлены в `models/test_constructor.py` (для обратной совместимости тестов)
- `tests.py` line 226 — `UnboundLocalError` `test_svc = test_svc.TestService` → `svc = test_svc.TestService`
- **Constraint attempts:** unique `(user_id, test_id)` → partial unique index PostgreSQL `WHERE status = 'in_progress'` (Alembic миграция)
- **Error handler:** `app/api/errors.py` — в `request_validation_handler` добавлена обработка `bytes` body (ASGI краш "Object of type bytes is not JSON serializable")
- **Cleanup:** удалён unreachable code после `return` в `app/services/test_service.py`, убран unused import `SAEnum` в `models/test_constructor.py`

## Frontend changes

### Новые компоненты (shared)
- `TestCard` — единая карточка теста (catalog + my-tests)
- `SkeletonCard` / `SkeletonList` — скелетоны загрузки
- `EmptyState` — пустое состояние с иконкой, заголовком, action
- `Loading` / `InlineLoading` — индикаторы загрузки
- `BackButton` — кнопка "Назад"
- `QuestionPoolModal` — модалка выбора вопроса из пула

### Экраны
- `CatalogPage` — переписан на DRY, TestCard, SkeletonList
- `MyTestsPage` — переписан на DRY, TestCard, фильтрация all/public/private
- `HistoryPage` — trend indicator (7-day avg), календарь GitHub-style
- `TestViewPage` — TypstRender для описания, stats карточки, attempts таблица
- `AnswerBlocks` — collapse/expand explanation (accordion с ChevronDown/Up)
- `TakeTestPage` — QuestionPool (`onAddFromPool`), summary screen при finish

### SDK
- Перегенерирован из OpenAPI через `@hey-api/openapi-ts` **без --client**
- Встроенный fetch-клиент (не axios)
- Авторизация: `localStorage.getItem('access_token')` через getter в `client/utils.gen.ts`
- Base URL: `http://localhost:8023`

### Auth
- Zustand store (`entities/user/model/store.ts`) с persist middleware
- Key: `user-store` в localStorage (хранит `user` + `token`)
- `useAuth` hook — token из Zustand, не из raw localStorage
- `__setAuth(token, user)` — глобальная helper для Cypress injection

### Исправления
- **TakeTestPage init attempt:** перед `startAttemptApiV1AttemptsPost` добавлен вызов `getActiveAttemptApiV1AttemptsActiveGet`. Если `has_active`, используется существующая попытка вместо создания новой (fix дублирования active attempt)
- **Cypress seeded-data:** исправлены селекторы кнопок под текущий UI (`Next` / `Finish` / `Submit All` вместо `Следующий` / `Завершить`); селектор `div[class*="basis-"]` с `force: true` для invisible parent
- **Removed dead code:** `axios.ts`, `features/auth/api/api-real.ts`, unused deps (`axios`, `react-beautiful-dnd`, `@hello-pangea/dnd`, `simple-icons`, `@testing-library/user-event`, `@types/react-beautiful-dnd`)

## Cypress E2E

### Custom commands (`cypress/support/e2e.ts`)
- `cy.loginAs('teacher' | 'student')` — API login → `__setAuth()` injection
- `cy.logout()` — чистка Zustand + reload
- `cy.step(name)` — logging
- `cy.api(method, path, body?)` — authenticated HTTP через `Cypress.env('TOKEN')`

### Тестируемые сценарии
| # | Сценарий | Статус |
|---|---|---|
| 1 | Teacher login + auth persist after reload | ✅ PASS |
| 2 | Student login + search input visible | ✅ PASS |
| 3 | Catalog: 6 seeded tests visible | ✅ PASS |
| 4 | Catalog: tag filter (math → URL includes tags=math) | ✅ PASS |
| 5 | Catalog click → navigate to test view | ✅ PASS |
| 6 | Teacher sees edit/settings/stats on own test | ✅ PASS |
| 7 | Student takes Math test + finish | ✅ PASS |
| 8 | Student history: calendar + attempts | ✅ PASS |
| 9 | Teacher My Tests: all 6 tests | ✅ PASS |
| 10 | Student review completed attempt | ✅ PASS |
| 11 | Teacher add question from pool | ✅ PASS |

**Score: 11/11 passing**
