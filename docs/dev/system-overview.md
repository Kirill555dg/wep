# Архитектура системы WEP

Общий обзор архитектуры Web Education Platform.

## Назначение системы

WEP LMS - веб-система для организации учебного процесса, в которой:

- **Преподаватель** управляет классами, уроками, домашними заданиями и базой задач, анализирует прогресс
- **Студент** вступает в классы, проходит уроки, выполняет домашние задания, видит личный прогресс
- Система предоставляет коммуникации (чат класса) и статистику

## Основные компоненты

```
┌─────────────────┐
│   Web Client    │  Frontend SPA (React + TypeScript)
│   (Frontend)    │
└────────┬────────┘
         │ REST + WebSocket
         ↓
┌─────────────────┐
│   Backend API   │  Domain Service (FastAPI)
│  (Domain Logic) │
└────────┬────────┘
         │ SQL
         ↓
┌─────────────────┐
│   PostgreSQL    │  Relational Database
│   (Database)    │
└─────────────────┘

┌─────────────────┐
│   Redis Pub/Sub │  (Optional) Realtime broker
└─────────────────┘
```

### Web Client (Frontend SPA)

- **Роль**: интерфейс пользователя и оркестратор пользовательских сценариев
- **Функции**:
  - Представление сценариев teacher/student
  - Визуализация данных и аналитики
  - Управление клиентским состоянием
  - Realtime UX для чата
- **Интерфейсы**:
  - REST/HTTP(S): запросы к backend API
  - WebSocket: realtime-канал чата

### Backend API (Domain Service)

- **Роль**: доменное ядро и публичный API системы
- **Функции**:
  - Проверка прав доступа и ролей
  - Реализация use-cases (классы, уроки, ДЗ, задачи, попытки, прогресс, чат)
  - Публикация стабильного контракта API (REST + WS)
  - Интеграция с хранилищем данных
- **Интерфейсы**:
  - REST/HTTP(S): публичные endpoints
  - WebSocket: канал чата
  - SQL: доступ к БД

### PostgreSQL Database

- **Роль**: персистентный источник истины по доменной модели
- **Функции**:
  - Хранение доменных сущностей (пользователи, классы, уроки, ДЗ, задачи, статистика, сообщения)
  - Обеспечение целостности (ограничения, связи, индексы)
- **Интерфейсы**:
  - SQL: взаимодействие только через backend

### Redis Pub/Sub Broker (Optional)

- **Роль**: масштабирование realtime (чат) при нескольких инстансах backend
- **Интерфейсы**:
  - Pub/Sub: backend ↔ Redis

## Характер взаимодействия

### Инициаторы запросов

- **Пользователь** → инициирует действия через UI
- **Frontend** → REST запросы к backend, WebSocket подключение
- **Backend** → ответы на REST, push-события в WebSocket

### Передаваемые данные

- **REST (Frontend → Backend)**: команды и запросы в JSON DTO
- **REST (Backend → Frontend)**: доменные данные в JSON DTO, paginated-ответы, error-ответы
- **WebSocket (Frontend ↔ Backend)**: события чата
- **Backend ↔ Database**: доменные операции через SQL

### Протоколы

- **HTTP(S) + JSON** - основной протокол UI ↔ API
- **WebSocket** - realtime-канал для чата
- **SQL** - backend ↔ DB
- **Pub/Sub** - backend ↔ Redis (опционально)

## Архитектурные подходы

### Backend: Clean Architecture

Слои (зависимости направлены внутрь):
- **API Layer**: REST/WebSocket endpoints
- **Service Layer**: бизнес-логика use-cases
- **Repository Layer**: доступ к данным
- **Models**: ORM модели

### Frontend: Feature-Sliced Design

Слои (зависимости направлены вниз):
- **app**: bootstrap, роутинг, guards
- **pages**: маршрутизируемые экраны
- **widgets**: композитные блоки UI
- **features**: сценарии пользователя
- **entities**: доменные данные на клиенте
- **shared**: ui-kit, api, utils

## Безопасность

- **Аутентификация**: JWT токены
- **Авторизация**: role-based (teacher/student)
- **Пароли**: Argon2id hashing
- **CORS**: настраиваемый список origins

## Масштабируемость

- **Backend**: stateless, можно запустить несколько инстансов за load balancer
- **Realtime**: Redis Pub/Sub для fanout между инстансами
- **Database**: connection pooling, индексы
- **Frontend**: SPA, CDN для статики
