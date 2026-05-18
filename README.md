# WEP — Интерактивный конструктор образовательных тестов

Веб-приложение для создания, проведения и автоматической проверки образовательных тестов с поддержкой математических формул (Typst), мультимедийного контента и публичного каталога.

**Ветка курсовой работы:** [`prksp_coursework`](https://github.com/Kirill555dg/wep/tree/prksp_coursework)

## Возможности

- Конструктор вопросов с Typst-рендерингом формул прямо в браузере
- Типы вопросов: одиночный/множественный выбор, текст, соответствие, загрузка файла
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
├── backend/               # FastAPI-приложение
│   ├── app/               # api, services, models, repositories
│   ├── alembic/           # Миграции БД
│   ├── .env.example       # Шаблон переменных окружения для backend
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/              # React-приложение
│   ├── src/               # FSD: app, pages, widgets, features, entities, shared
│   ├── .env.example       # Шаблон переменных окружения для frontend
│   ├── nginx-prod.conf    # Nginx-конфиг для продакшн-образа (нужно сменить домен)
│   ├── Dockerfile.prod
│   └── package.json
├── deploy/                # Docker Compose
│   ├── .env.example       # Шаблон переменных окружения для docker-compose
│   ├── docker-compose.yml          # dev (только инфраструктура: Postgres + MinIO)
│   └── docker-compose.prod.yml     # продакшн (все сервисы)
└── coursework/            # Курсовая работа (Typst)
```

---

## Локальная разработка

### 1. Запустить инфраструктуру (PostgreSQL + MinIO)

```bash
cd deploy
cp .env.example .env      # значения по умолчанию подходят для dev
docker compose up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env      # DATABASE_URL, SECRET_KEY, MINIO_* уже заполнены для dev
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8023
```

- API: `http://localhost:8023`
- Swagger: `http://localhost:8023/api/docs`

### 3. Frontend

```bash
cd frontend
cp .env.example .env      # VITE_API_URL оставить пустым (прокси через nginx) или
                          # раскомментировать строку с localhost для dev без Docker
bun install
bun run dev
```

- Приложение: `http://localhost:5174`

---

## Развёртывание в продакшн

> **Быстрый старт:** после клонирования запустите `bash setup.sh` — скрипт установит Docker, запросит домен и пароли, настроит SSL, соберёт образы и применит миграции.

### Ручная установка

#### Требования

- VPS с Docker и Docker Compose (Ubuntu 22.04+)
- Домен с A-записью, указывающей на IP сервера
- Открытые порты 80 и 443

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Kirill555dg/wep.git -b prksp_coursework
cd wep
```

### 2. Получить SSL-сертификат

```bash
apt install -y certbot
certbot certonly --standalone -d your-domain.example
```

Сертификат будет сохранён в `/etc/letsencrypt/live/your-domain.example/`.

### 3. Прописать домен в Nginx-конфиге

Файл `frontend/nginx-prod.conf` содержит `your-domain` — заменить на реальный домен:

```bash
sed -i 's/your-domain/your-domain.example/g' frontend/nginx-prod.conf
```

### 4. Создать `.env` для docker-compose

```bash
cp deploy/.env.example deploy/.env
nano deploy/.env
```

Минимальный `deploy/.env` для продакшна:

```env
POSTGRES_USER=wep
POSTGRES_PASSWORD=<надёжный пароль>
POSTGRES_DB=wep_db

SECRET_KEY=<вывод: python3 -c "import secrets; print(secrets.token_hex(32))">

MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=<надёжный пароль>
MINIO_BUCKET=wep-media
MINIO_PUBLIC_URL=https://your-domain.example/media

BACKEND_CORS_ORIGINS=["https://your-domain.example"]
```

### 5. Собрать и запустить

```bash
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
```

### 6. Применить миграции БД

```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 7. Проверить

```bash
docker compose -f docker-compose.prod.yml ps
curl https://your-domain.example/api/v1/health
```

Ожидаемый ответ: `{"status": "ok"}`.

### Обновление

```bash
git pull origin prksp_coursework
cd deploy
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## Переменные окружения

Переменные окружения разделены по двум файлам:

### `deploy/.env` — для docker-compose и backend-контейнера

| Переменная | Описание |
|---|---|
| `POSTGRES_USER` | Пользователь PostgreSQL |
| `POSTGRES_PASSWORD` | Пароль PostgreSQL |
| `POSTGRES_DB` | Имя базы данных |
| `SECRET_KEY` | Секрет для подписи JWT (64+ символа) |
| `MINIO_ACCESS_KEY` | Логин MinIO |
| `MINIO_SECRET_KEY` | Пароль MinIO |
| `MINIO_BUCKET` | Имя бакета для медиафайлов |
| `MINIO_PUBLIC_URL` | Публичный URL бакета (`https://домен/media`) |
| `BACKEND_CORS_ORIGINS` | JSON-массив разрешённых CORS-источников |

### `frontend/.env` — для сборки фронтенда

| Переменная | Описание |
|---|---|
| `VITE_API_URL` | URL бэкенда. Пустая строка — запросы через nginx на том же домене (продакшн). `http://localhost:8023/api` — для dev без Docker. |

---

Миркин К.Л., ИКБО-10-23, РТУ МИРЭА, 2026
