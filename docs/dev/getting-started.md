# Быстрый старт для разработчиков

Инструкция по развертыванию локального окружения для разработки.

## Требования

- Python 3.12+
- Node.js 18+
- PostgreSQL 16
- Redis 7 (опционально)
- Git

## Клонирование репозитория

```bash
git clone https://github.com/kerrodar/wep.git
cd wep
```

## Вариант 1: Docker Compose (рекомендуется)

```bash
cd deploy
cp .env.example .env
# Отредактировать .env

docker-compose up -d
```

Доступ:
- Backend: http://localhost:8023
- PostgreSQL: localhost:5433

## Вариант 2: Локальная разработка

### Backend

```bash
cd backend

# Создать виртуальное окружение и установить зависимости
uv venv
uv pip install -r requirements.txt -r requirements-dev.txt

# Настроить .env
cp .env.example .env
# Отредактировать DATABASE_URL и другие параметры

# Применить миграции
uv run alembic upgrade head

# Запустить сервер
uv run uvicorn app.main:app --host 0.0.0.0 --port 8023 --reload
```

Backend доступен на http://localhost:8023

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Настроить .env
cp .env.example .env
# Отредактировать VITE_API_URL

# Запустить dev-сервер
npm run dev
```

Frontend доступен на http://localhost:5173

## PostgreSQL

Если используете локальный PostgreSQL:

```bash
# Создать базу данных
createdb wep_education

# Создать пользователя
psql -c "CREATE USER wep_user WITH PASSWORD 'wep_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE wep_education TO wep_user;"
```

## Redis (опционально)

Для realtime чата:

```bash
# macOS
brew install redis
brew services start redis

# Linux
sudo apt install redis-server
sudo systemctl start redis
```

## Проверка установки

### Backend

```bash
# API docs
open http://localhost:8023/api/docs

# Health check
curl http://localhost:8023/api/health
```

### Frontend

```bash
open http://localhost:5173
```

## Следующие шаги

- [Архитектура системы](system-overview.md)
- [Backend архитектура](backend/arch.md)
- [Frontend архитектура](frontend/arch.md)
- [Rest API](api/rest-api.md)
- [Backend — руководство разработчика](backend/guide.md)
- [Frontend — руководство разработчика](frontend/guide.md)
