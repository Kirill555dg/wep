# E2E тестирование WEP (Cypress)

## Запуск

```bash
# Требует запущенного backend + frontend
cd frontend
bun run test:e2e        # headless прогон
bun run cypress          # открыть Cypress UI
```

Или вручную:
```bash
cd deploy && docker compose up -d
cd ../backend && uv run uvicorn app.main:app --reload --port 8023 &
cd ../frontend && bun run dev &
```

## Тестовые данные (seeded)

- `teacher@wep.dev` / `TeacherPass123!` — автор 6 тестов
- `student@wep.dev` / `StudentPass123!` — 3 завершённые попытки

Файл `cypress/fixtures/user.json` хранит teacher-данные.

## Custom Commands

Файл `cypress/support/e2e.ts`:

| Команда | Описание |
|---|---|
| `cy.loginAs('teacher' \| 'student')` | API-логин + Zustand injection через `__setAuth` |
| `cy.logout()` | Очистка Zustand + reload |
| `cy.api(method, path, body?)` | Аутентифицированный HTTP через `Cypress.env('TOKEN')` |
| `cy.step(name)` | Логирование шага |

## Покрытые сценарии (seeded-data.cy.ts)

1. **Авторизация**
   - Teacher login + persist после reload ✅
   - Student login + поиск виден ✅
2. **Каталог**
   - Видны 6 seeded тестов ✅
   - Фильтр по тегу (math) меняет URL ✅
   - Клик карточки → страница теста ✅
3. **Страница теста**
   - Автор видит кнопки "Редактировать / Настройки / Статистика" ✅
4. **Прохождение теста**
   - Cleanup активной попытки через API
   - Переход `/tests/3/take`
   - Ответы: Single Choice, Text
   - Завершение и проверка `/attempts/{id}`
5. **История**
   - Отображение календаря и последних попыток
6. **Мои тесты**
   - Все 6 тестов teacher видит в списке ✅
7. **Результаты**
   - Просмотр завершённой попытки ✅
8. **База вопросов**
   - Добавление вопроса из пула в тест ✅

## Известные проблемы и фиксы

### Проблема: duplicate active attempt (422 на POST /attempts/)
**Причина:** unique constraint `(user_id, test_id)` блокировал повторные попытки даже для завершённых.
**Fix:** partial unique index PostgreSQL `WHERE status = 'in_progress'`.
**Commit:** миграция alembic, обновление `app/models/test_constructor.py`.

### Проблема: `TypeError: Object of type bytes is not JSON serializable`
**Причина:** `RequestValidationError.body` содержал `bytes`, который попадал в debug-meta.
**Fix:** `app/api/errors.py` — проверка `isinstance(body, bytes)` с decode в UTF-8.

### Проблема: TakeTestPage создаёт вторую попытку при навигации
**Причина:** `TestViewPage` создавал attempt, но `TakeTestPage` не знал о нём (localStorage пуст).
**Fix:** в `TakeTestPage.tsx` перед `startAttemptApiV1AttemptsPost` добавлена проверка `getActiveAttemptApiV1AttemptsActiveGet`. Если `has_active`, используется существующая попытка.

### Проблема: Cypress не находит кнопки "Следующий / Завершить"
**Причина:** UI перешёл на английские лейблы (`Next`, `Finish`, `Submit All`).
**Fix:** обновлены селекторы в `cypress/e2e/seeded-data.cy.ts`.

### Проблема: клик на `div[class*="basis-"]` invisible в Cypress
**Причина:** родительский `div` имеет `class="contents"` (0×0).
**Fix:** `cy.get('div[class*="basis-"]').first().click({ force: true })`.

## Рекомендации по расширению тестов

- Генерация UUID внутри сценариев для идемпотентности (уникальные названия тестов, email-адреса).
- Cleanup через `cy.api('DELETE', ...)` после каждого сценария создания.
- Тестирование медиа: загрузка BMP и WAV через `cy.fixture` + `cy.request`.
- Тестирование ограничения по времени: проверка автозавершения через `cy.clock`.
