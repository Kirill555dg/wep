# Health Checker

CLI-утилита для проверки работоспособности инфраструктуры WEP (PostgreSQL, MinIO, миграции, API).

## Использование

```bash
# Через uv (из папки tools/health_checker/)
uv run python -m health_checker

# Через установленный бинарник (после сборки)
health-checker

# С собственными параметрами
health-checker --database-url postgresql://user:pass@host:5432/db
```

## Параметры

| Флаг | Переменная окружения | По умолчанию | Описание |
|---|---|---|---|
| `--database-url` | `DATABASE_URL` | `postgresql://wep_user:wep_password@localhost:5433/wep_education` | URL PostgreSQL |
| `--minio-endpoint` | `MINIO_ENDPOINT` | `127.0.0.1:9000` | MinIO endpoint |
| `--minio-access-key` | `MINIO_ACCESS_KEY` | `minioadmin` | MinIO access key |
| `--minio-secret-key` | `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret key |
| `--minio-secure` | `MINIO_SECURE` | `false` | Флаг: использовать HTTPS для MinIO |
| `--api-url` | `API_URL` | `http://localhost:8023` | URL API (проверка health endpoint) |
| `--verbose`, `-v` | — | — | Подробный вывод |

## Проверки

1. **PostgreSQL** — подключение, `SELECT current_schema()`
2. **MinIO** — подключение, список bucket'ов
3. **Migrations** — версия миграции из `alembic_version`
4. **API** — GET `/` с version

## Exit codes

- `0` — все проверки пройдены
- `1` — одна или несколько проверок не прошли

## Сборка standalone-бинарника

```bash
cd tools/health_checker
./build.sh
```

Результат: `tools/health_checker/dist/health-checker` — бинарник можно скопировать на любую машину с той же ОС и запустить.

## Установка глобально через uv

```bash
cd tools/health_checker
uv tool install .
# или
uv tool install --editable .
```

После этого `health-checker` доступен в PATH.
