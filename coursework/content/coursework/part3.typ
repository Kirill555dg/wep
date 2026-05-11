#import "../../const.typ"

= Разработка архитектуры приложения на основе Clean Architecture

== Применение Clean Architecture к серверной части

На основе выбранного архитектурного паттерна спроектирована архитектура серверной части системы управления обучением. Архитектура организована в соответствии с принципом разделения на концентрические слои, где каждый слой имеет строго определённую зону ответственности, а зависимости направлены внутрь — от внешних инфраструктурных компонентов к внутренней бизнес-логике @martin2021. Принцип многослойной организации, общие подходы к разделению логики и управлению зависимостями в сложных программных системах также подробно рассматриваются в литературе по архитектуре информационных систем @vodyakho2022.

В рамках разработанной архитектуры выделены следующие слои:

- *API Layer (Controllers)* — внешний слой, отвечающий за приём HTTP-запросов, валидацию входных данных через Pydantic-схемы и формирование HTTP-ответов. Реализован с использованием FastAPI-роутеров. Не содержит бизнес-логики, только делегирование вызовов сервисному слою.

- *Service Layer (Use Cases)* — слой бизнес-логики, реализующий сценарии использования системы. Каждый сервис инкапсулирует определённую функциональную область: аутентификация, управление классами, работа с уроками, домашними заданиями, тестирование и т.д. Сервисы не имеют прямых зависимостей от HTTP-контекста или базы данных, используя абстракции репозиториев.

- *Repository Layer (Interface Adapters)* — слой доступа к данным, реализующий паттерн Repository. Предоставляет интерфейсы для выполнения операций CRUD и специфических запросов, скрывая детали реализации SQLAlchemy ORM.

- *Models Layer (Frameworks & Drivers)* — самый внутренний инфраструктурный слой, содержащий определения ORM-моделей, конфигурацию базы данных, настройки миграций и внешние интеграции (Redis для realtime-чата).

Правило зависимостей (Dependency Rule) соблюдается следующим образом: API-слой зависит от Service-слоя, Service-слой зависит от Repository-слоя, Repository-слой использует Models. Модели не зависят ни от какого другого слоя проекта. Обратные зависимости исключены — ни один внутренний слой не импортирует компоненты внешних слоёв.

Данная организация кода реализована в структуре директорий серверного приложения:

```
app/
├── main.py                    # Entry point
├── api/                       # API Layer
│   ├── v1/                   #  REST endpoints
│   ├── dependencies.py       #  Dependency Injection
│   ├── errors.py             #  Обработка ошибок
│   ├── openapi.py            #  Настройка OpenAPI
│   └── middleware/           #  Middleware (CORS, request_id)
├── services/                  # Service Layer (бизнес-логика)
│   ├── auth.py               #  Аутентификация
│   ├── classroom.py           #  Управление классами
│   ├── lesson.py             #  Управление уроками
│   ├── homework.py           #  Домашние задания
│   ├── problem.py            #  База задач
│   ├── testing.py            #  Приём ответов, проверка
│   ├── result.py             #  Статистика и прогресс
│   ├── theory.py             #  Теоретические материалы
│   └── chat.py               #  Чат класса
├── repositories/             # Repository Layer (доступ к данным)
│   ├── base.py               #  Базовый репозиторий (CRUD)
│   ├── user.py               #  Пользователи
│   ├── classroom.py          #  Классы
│   ├── lesson.py             #  Уроки
│   ├── homework.py           #  Домашние задания
│   └── communication.py     #  Чат и сообщения
├── models/                   # Models Layer (ORM)
│   ├── users.py              #  Таблицы пользователей
│   ├── classes.py            #  Учебные классы
│   ├── lessons.py            #  Уроки
│   ├── homework.py           #  Домашние задания
│   ├── problems.py           #  Задачи
│   ├── theory.py             #  Теоретические материалы
│   ├── files.py              #  Файлы
│   └── communication.py     #  Сообщения чата
├── schemas/                   # Pydantic DTO
├── core/                      # Конфигурация и утилиты
│   ├── config.py             #  Настройки (.env)
│   ├── security.py           #  Argon2 + JWT
│   └── pagination.py         #  Пагинация
├── db/                        # База данных
│   ├── session.py            #  AsyncSession
│   └── url.py                #  URL-хелперы
├── domain/                    # Доменные ошибки
├── realtime/                  # WebSocket и Redis Pub/Sub
└── scripts/                   # Утилиты (seed, export OpenAPI)
```

Таким образом, структура директорий непосредственно отражает выбранную Clean Architecture. Каждый слой размещён в отдельном пакете, и зависимости строго направлены от внешних пакетов к внутренним.

== Dependency Injection как механизм связывания слоёв

Ключевым механизмом, обеспечивающим соблюдение правила зависимостей в разработанной архитектуре, является Dependency Injection (DI). FastAPI предоставляет встроенную поддержку DI через механизм зависимостей (Depends), который используется для связывания слоёв без создания жёстких зависимостей между ними.

На уровне API создаются функции-фабрики, которые конструируют сервисы с необходимыми зависимостями. Пример реализации DI для аутентификации приведён в листинге @di-example.

#figure(
  ```python
  # app/api/dependencies.py
  from fastapi import Depends
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.db.session import get_db
  from app.services.auth import AuthService
  from app.repositories.user import UserRepository

  async def get_auth_service(
      db: AsyncSession = Depends(get_db),
  ) -> AuthService:
      return AuthService(db)

  async def get_current_user(
      credentials: HTTPAuthorizationCredentials = Depends(security),
      db: AsyncSession = Depends(get_db),
  ) -> User:
      """Извлекает и проверяет JWT-токен, возвращает пользователя."""
      payload = decode_access_token(credentials.credentials)
      user_repo = UserRepository(db)
      user = await user_repo.get_by_id(int(payload["sub"]))
      if not user:
          raise HTTPException(status_code=401)
      return user
  ```,
  caption: [Реализация Dependency Injection для сервисов аутентификации],
) <di-example>

В данном листинге показано, как Dependency Injection позволяет инстанцировать сервисы с их зависимостями (сессия базы данных, репозитории) без создания глобальных переменных или жёстких связей. Каждый тест может подставить свою реализацию репозитория, заменив реальную базу данных на mock.

== Диаграмма компонентов архитектуры

На рисунке @components-diagram представлена диаграмма компонентов архитектуры, отражающая взаимодействие между слоями системы. Внешний слой (API Controller) принимает HTTP-запросы от клиента и делегирует выполнение бизнес-операций соответствующим сервисам. Сервисы используют репозитории для доступа к данным, а репозитории выполняют SQL-запросы через ORM SQLAlchemy к СУБД PostgreSQL.

#figure(
  image("../../assets/components-diagram.png", width: 100%),
  caption: [Диаграмма основных компонентов системы, отражающая Clean Architecture],
) <components-diagram>

Ключевые компоненты серверной части включают:
- *API Controller* — точка входа для HTTP-запросов, маршрутизация и валидация.
- *AuthService* — аутентификация и сессия (JWT + Argon2).
- *ClassroomService* — управление классами и членством.
- *LessonService* — управление уроками.
- *HomeworkService* — управление домашними заданиями.
- *ProblemService* — база задач (создание, редактирование).
- *TestingService* — приём ответов и автоматическая проверка.
- *ResultService* — статистика и прогресс.
- *ChatService* — хранение и выдача истории сообщений.
- *Realtime chat runtime* — WebSocket для чата в реальном времени.
- *Repositories* — слой доступа к данным.

Каждый сервис соответствует одному use case (сценарию использования) и реализует бизнес-логику независимо от HTTP-контекста.

== Проектирование базы данных

Спроектирована реляционная база данных, охватывающая все ключевые сущности предметной области: пользователей, учебные классы, уроки, домашние задания, задачи, результаты тестирования и сообщения чата. ER-диаграмма данных представлена на рисунке @er-diagram.

#figure(
  image("../../assets/er-diagram.png", width: 100%),
  caption: [ER-диаграмма данных системы управления обучением],
) <er-diagram>

Основные сущности базы данных включают:

- *user* — центральная сущность системы, хранящая общие данные пользователя (имя, email, аватар).
- *login_data* — изолированные данные аутентификации (хеш пароля Argon2).
- *teacher* и *student* — специализированные сущности с дополнительными атрибутами для соответствующих ролей.
- *class_group* — учебный класс, объединяющий студентов под руководством преподавателя.
- *lesson* — урок в рамках класса (тема, порядковый номер, статус публикации).
- *homework* — домашнее задание, привязанное к уроку.
- *problem* — задача, которая может быть использована в разных домашних заданиях (связь \"многие ко многим\").
- *statistics* — результат выполнения задачи студентом (ответ, статус проверки, количество попыток).
- *chat* и *message* — чат класса и сообщения.
- *invite* — приглашение в класс.
- *themes* — иерархия тем для структурирования учебного контента.

Реализация ORM-моделей выполнена с использованием SQLAlchemy с асинхронным драйвером asyncpg. Пример модели пользователя приведён в листинге @user-model-example.

#figure(
  ```python
  # app/models/users.py
  from sqlalchemy import Column, String, Boolean, DateTime
  from sqlalchemy.dialects.postgresql import UUID
  from sqlalchemy.orm import relationship
  from app.db.session import Base
  import uuid
  from datetime import datetime, timezone

  class User(Base):
      __tablename__ = "user"

      id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
      username = Column(String(50), unique=True, nullable=False, index=True)
      email = Column(String(255), unique=True, nullable=False, index=True)
      first_name = Column(String(100), nullable=False)
      last_name = Column(String(100), nullable=False)
      avatar_url = Column(String(500), nullable=True)
      is_active = Column(Boolean, default=True)
      created_at = Column(
          DateTime(timezone=True),
          default=lambda: datetime.now(timezone.utc),
      )
  ```,
  caption: [ORM-модель пользователя (SQLAlchemy)],
) <user-model-example>

== Выводы по главе

В данной главе разработана детальная архитектура серверной части системы управления обучением на основе Clean Architecture. Описаны четыре слоя архитектуры: API, Service, Repository и Models, их зоны ответственности и взаимодействие. Приведена структура директорий проекта, непосредственно отражающая выбранный архитектурный паттерн.

Описана реализация Dependency Injection как механизма связывания слоёв, обеспечивающего слабую связанность и тестируемость компонентов. Приведена диаграмма компонентов, отражающая распределение ответственности между модулями системы.

Спроектирована реляционная база данных, охватывающая все ключевые сущности предметной области. ER-диаграмма и пример ORM-модели демонстрируют применение Clean Architecture на уровне работы с данными. Разработанная архитектура является основой для реализации серверной части в следующей главе.
