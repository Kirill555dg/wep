# WEP — Интерактивный конструктор образовательных тестов

Веб-приложение для создания, проведения и автоматической проверки образовательных тестов с поддержкой математических формул (Typst), мультимедийного контента и публичного каталога.

**Ветка курсовой работы:** [`prksp_coursework`](https://github.com/Kirill555dg/wep/tree/prksp_coursework)

## Возможности

- Конструктор вопросов с Typst-рендерингом формул прямо в браузере
- Типы вопросов: одиночный/множественный выбор, текстовый ответ, соответствие, загрузка файла
- Прикрепление медиафайлов к вопросам (изображения, аудио, видео)
- Публичный каталог тестов с поиском по тегам; приватный доступ по ссылке
- Автоматическая проверка ответов и статистика прохождений
- Хранение медиафайлов в S3-совместимом хранилище MinIO

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, MinIO |
| Frontend | React 18, TypeScript, Vite, TanStack Query, Zustand, Radix UI, Tailwind CSS, typst.ts |
| Инфраструктура | Docker Compose, Nginx |

## Структура репозитория

```
wep/
├── backend/          # FastAPI-приложение
│   ├── app/          # api, services, models, repositories
│   ├── alembic/      # Миграции БД
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/         # React-приложение
│   ├── src/          # FSD: app, pages, widgets, features, entities, shared
│   ├── Dockerfile.prod
│   └── package.json
├── deploy/           # Docker Compose
│   ├── docker-compose.yml       # dev (только инфраструктура)
│   └── docker-compose.prod.yml  # продакшн
└── coursework/       # Курсовая работа (Typst)
```

## Локальная разработка

### 1. Запустить инфраструктуру (PostgreSQL + MinIO)

```bash
cd deploy
cp .env.example .env   # заполнить значения
docker compose up -d
```

### 2. Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8023
```

Backend: `http://localhost:8023`  
Документация API: `http://localhost:8023/api/docs`

### 3. Frontend

```bash
cd frontend
bun install
bun run dev
```

Frontend: `http://localhost:5174`

---

## Развёртывание в продакшн

### Требования

- VPS с Docker и Docker Compose (Ubuntu 22.04+)
- Домен с A-записью на IP сервера
- Открытые порты 80 и 443

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Kirill555dg/wep.git -b prksp_coursework
cd wep
```

### 2. Создать `.env`

```bash
nano deploy/.env
```

```env
POSTGRES_USER=wep
POSTGRES_PASSWORD=<надёжный пароль>
POSTGRES_DB=wep_db

SECRET_KEY=<случайная строка 64+ символа>

MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=<надёжный пароль>
MINIO_BUCKET=wep-media
MINIO_PUBLIC_URL=https://<ваш-домен>/media

BACKEND_CORS_ORIGINS=https://<ваш-домен>
```

### 3. Получить SSL-сертификат

```bash
apt install -y certbot
certbot certonly --standalone -d <ваш-домен>
```

### 4. Запустить

```bash
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. Проверить

```bash
docker compose -f docker-compose.prod.yml ps
curl https://<ваш-домен>/api/v1/health
```

### Обновление

```bash
git pull origin prksp_coursework
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Переменные окружения

| Переменная | Описание |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Параметры подключения к PostgreSQL |
| `SECRET_KEY` | Секрет для подписи JWT-токенов (64+ символа) |
| `MINIO_ACCESS_KEY` / `MINIO_SECRET_KEY` | Учётные данные MinIO |
| `MINIO_BUCKET` | Имя бакета для хранения медиафайлов |
| `MINIO_PUBLIC_URL` | Публичный URL бакета (для presigned-ссылок) |
| `BACKEND_CORS_ORIGINS` | Разрешённые CORS-источники (домен фронтенда) |

---

Миркин К.Л., ИКБО-10-23, РТУ МИРЭА, 2026
