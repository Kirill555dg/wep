# Backend архитектура

Детальное описание архитектуры серверной части WEP.

## Назначение backend

Backend - серверный доменный компонент LMS, который:

- Экспонирует публичный контракт системы (REST API + WebSocket)
- Реализует бизнес-правила учебной платформы
- Обеспечивает целостность данных через транзакции
- Формирует DTO-контракты (Pydantic-схемы)
- Служит источником OpenAPI контракта

## Clean Architecture

Зависимости направлены внутрь (от внешних слоев к внутренним):

```
┌────────────────────────────────────┐
│      API Layer (FastAPI)           │  HTTP/WebSocket endpoints
└────────────┬───────────────────────┘
             │ depends on
┌────────────▼───────────────────────┐
│      Service Layer                 │  Business logic
└────────────┬───────────────────────┘
             │ depends on
┌────────────▼───────────────────────┐
│      Repository Layer              │  Data access
└────────────┬───────────────────────┘
             │ depends on
┌────────────▼───────────────────────┐
│      Models (ORM)                  │  Database schema
└────────────────────────────────────┘
```

## Компоненты по слоям

### API Layer (`app/api/v1/`)

**Роль**: Публичный входной слой - маршрутизация HTTP/WS запросов

**Ответственность**:
- Принимают запросы (HTTP)
- Валидируют входные DTO
- Получают зависимости через DI
- Вызывают сервисы
- Возвращают DTO-ответы

**Модули**:
- `auth.py` - аутентификация, регистрация
- `classrooms.py` - управление классами, чат
- `lessons.py` - уроки
- `homework.py` - домашние задания
- `problems.py` - база задач
- `testing.py` - выполнение ДЗ
- `statistics.py` - статистика
- `health.py` - health checks

### Service Layer (`app/services/`)

**Роль**: Бизнес-логика и use-cases

**Основные сервисы**:

- `AuthService` - регистрация/логин, управление ролью, JWT
- `ClassroomService` - создание/обновление классов, инвайт-коды
- `LessonService` - управление уроками
- `HomeworkService` - сборка ДЗ из задач
- `ProblemService` - управление базой задач
- `TestingService` - приём ответов, автопроверка
- `ResultService` - агрегирование статистики
- `ChatService` - чат класса

**Принципы**:
- Один сервис = одна доменная область
- Не содержат SQL/ORM логику
- Работают с репозиториями
- Возвращают DTO или доменные объекты

### Repository Layer (`app/repositories/`)

**Роль**: Абстракция доступа к PostgreSQL

**Ответственность**:
- CRUD операции
- Фильтрации, join'ы, агрегаты
- Изоляция SQLAlchemy деталей

**Основные репозитории**:
- `UserRepository` - пользователи
- `ClassroomRepository` - классы
- `LessonRepository` - уроки
- `HomeworkRepository` - ДЗ
- `ProblemRepository` - задачи
- `StatisticsRepository` - статистика попыток
- `MessageRepository` - сообщения чата

**Базовый класс**:
```python
class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get(self, id: UUID) -> Model | None:
        ...
    
    async def create(self, data: dict) -> Model:
        ...
    
    async def update(self, id: UUID, data: dict) -> Model:
        ...
    
    async def delete(self, id: UUID) -> None:
        ...
```

### Models (`app/models/`)

**Роль**: ORM модели (SQLAlchemy)

**Основные модели**:

- Identity: `User`, `LoginData`, `Teacher`, `Student`
- Academic: `Classroom`, `StudentClassroom`, `Lesson`
- Content: `Problem`, `Homework`, `HomeworkProblem`
- Communication: `Chat`, `Message`
- Analytics: `Statistics`

### DTO/Schemas (`app/schemas/`)

**Роль**: Контракты на границе API

**Типы схем**:
- Request schemas - входные данные
- Response schemas - выходные данные
- Error schemas - формат ошибок
- Pagination schemas - Page[T]

### Realtime Subsystem (`app/realtime/`)

**Компоненты**:

- `ConnectionManager` - управление WebSocket соединениями
- `RedisPubSubBroker` - fanout между инстансами
- `presence.py` - presence/typing механика
- `auth.py` - авторизация WebSocket

### Infrastructure (`app/core/`, `app/db/`)

**Компоненты**:

- `config.py` - конфигурация (env variables)
- `security.py` - JWT, Argon2 hashing
- `session.py` - database session management
- `pagination.py` - пагинация defaults
- `errors.py` - доменные ошибки
- `middleware/` - CORS, request_id

## Ключевые потоки

### Аутентификация

```
Client → POST /auth/login
  → AuthService.login()
    → UserRepository.get_by_email()
    → verify_password()
    → create_access_token()
  ← JWT token
```

### Создание ДЗ (teacher)

```
Client → POST /homework
  → get_current_teacher() (dependency)
  → HomeworkService.create_homework()
    → ClassroomRepository.get() (проверка ownership)
    → HomeworkRepository.create()
    → HomeworkProblemRepository.bulk_create()
  ← HomeworkResponse
```

### Отправка ответа (student)

```
Client → POST /testing/submit-answer
  → get_current_student() (dependency)
  → TestingService.submit_answer()
    → HomeworkRepository.get() (проверка доступа)
    → ProblemRepository.get()
    → check_answer()
    → StatisticsRepository.update()
  ← StatisticsResponse
```

### Realtime чат

```
Client → WS /classrooms/{id}/chat/ws
  → authenticate_websocket()
  → ConnectionManager.connect()
  → listen for messages
    → on message received:
      → ChatService.save_message()
      → RedisPubSubBroker.publish() (if enabled)
      → ConnectionManager.broadcast()
```

## Технологический стек

- **Python 3.12+**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - async ORM
- **Alembic** - миграции БД
- **Pydantic V2** - валидация и сериализация
- **PostgreSQL 16** - основная БД
- **Redis 7** - Pub/Sub для realtime (опционально)
- **JWT** - аутентификация
- **Argon2** - хеширование паролей

## Безопасность

### Аутентификация и авторизация

- JWT токены с role claim
- Dependencies: `get_current_user`, `get_current_teacher`, `get_current_student`
- Проверка role_changed при каждом запросе

### Контроль доступа

- Teacher: может управлять только своими классами
- Student: может видеть только опубликованные уроки/ДЗ
- Проверки в Service Layer

### Безопасность данных

- Пароли: Argon2id hashing
- SQL injection: параметризованные запросы (SQLAlchemy)
- CORS: настраиваемый whitelist

## Тестирование

- Unit tests: pytest
- Integration tests: pytest + TestClient
- Database: pytest-asyncio + test database
- Coverage: pytest-cov
