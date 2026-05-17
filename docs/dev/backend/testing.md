# Тестирование бэкенда

## Полный воркфлоу

```bash
# 1. Запустить инфраструктуру (если ещё не запущена)
#    macOS: требуется Colima (brew install colima && colima start)
cd deploy
cp .env.example .env
docker compose up -d postgres minio

# 2. Установить зависимости
cd backend
uv venv
uv pip install -r requirements.txt -r requirements-dev.txt

# 3. Прогнать тесты
uv run pytest tests/
```

## Команды

```bash
# Все тесты (требует PostgreSQL + MinIO)
uv run pytest tests/

# Только unit + сервисные + HTTP (без фаззинга) — ~15s
uv run pytest tests/ --ignore=tests/fuzz

# Только Hypothesis фаззинг — ~30s
uv run pytest tests/fuzz/

# Один тест по имени
uv run pytest tests/ -k "login"

# Один файл с подробным трейсом
uv run pytest -x --tb=long tests/path/to_test.py
```

## Что проверяется

| Тест | Описание |
|------|----------|
| `test_infra.py` | PostgreSQL + MinIO доступны |
| `test_auth_service.py` | Регистрация, аутентификация, роли |
| `test_test_service.py` | CRUD тестов и вопросов |
| `test_attempt_service.py` | Попытки, ответы, оценки |
| `test_grading_service.py` | Логика оценивания (без БД) |
| `test_role_access.py` | Контроль доступа, ownership |
| `test_token_role_mismatch.py` | JWT токены со сменой роли |
| `fuzz/` | Property-based тесты (Hypothesis) |

## Важно

- Каждый тест работает в **изолированной PostgreSQL-схеме**, которая создаётся на старте и удаляется после завершения
- Тестам нужен **живой PostgreSQL** — `docker compose up -d postgres`
- MinIO требуется только для `test_infra.py` и HTTP-тестов media
- Конфигурация подключения берётся из переменной `DATABASE_URL` в `.env`
