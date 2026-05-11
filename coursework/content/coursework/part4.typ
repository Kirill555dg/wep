#import "../../const.typ"

= Разработка серверной части интернет-ресурса

== Реализация REST API на FastAPI

Серверная часть системы реализована на языке Python 3.12+ с использованием веб-фреймворка FastAPI, обеспечивающего асинхронную обработку запросов, автоматическую валидацию данных через Pydantic v2 @pydantic-docs и генерацию OpenAPI-спецификации @eliseev2024 @fastapi-docs. При проектировании API использованы стандартные подходы REST, описанные в специализированной литературе @alpatov2024. Архитектура серверной части полностью соответствует Clean Architecture, описанной в предыдущей главе.

REST API предоставляет следующие группы эндпоинтов, сгруппированные по функциональным областям:

- *Auth* — регистрация, аутентификация, получение профиля текущего пользователя (/api/v1/auth/register, /login, /me).
- *Classrooms* — управление классами: создание, получение списка, вступление по приглашению (/api/v1/classes/).
- *Lessons* — управление уроками: создание, публикация, получение содержимого (/api/v1/lessons/).
- *Homework* — домашние задания: создание, получение состава задач (/api/v1/homework/).
- *Problems* — база задач: создание, редактирование (/api/v1/problems/).
- *Testing* — приём ответов на задачи: отправка ответа, получение результата (/api/v1/testing/).
- *Statistics* — статистика выполнения: прогресс студента, результаты по классу (/api/v1/statistics/).
- *Theory* — теоретические материалы (/api/v1/theory/).
- *Chat* — сообщения чата класса (/api/v1/chat/).

При разработке эндпоинтов соблюдается принцип разделения ответственности: каждый эндпоинт делегирует выполнение бизнес-операции соответствующему сервису и не содержит бизнес-логики непосредственно. Пример реализации эндпоинта аутентификации приведён в листинге @auth-endpoint-example.

#figure(
  ```python
  # app/api/v1/auth.py
  import fastapi
  from fastapi import status as http_status
  from app.api import dependencies as deps
  from app.models import users as user_models
  from app.schemas import users as user_schemas
  from app.services import auth as auth_service_module

  router = fastapi.APIRouter()

  @router.post(
      "/register",
      response_model=user_schemas.UserResponse,
      status_code=http_status.HTTP_201_CREATED,
  )
  async def register(
      user_data: user_schemas.UserCreate,
      auth_service: auth_service_module.AuthService =
          fastapi.Depends(deps.get_auth_service),
  ) -> user_schemas.UserResponse:
      """Регистрация нового пользователя."""
      return await auth_service.register_user(user_data)

  @router.post("/login", response_model=user_schemas.TokenResponse)
  async def login(
      credentials: user_schemas.LoginRequest,
      auth_service: auth_service_module.AuthService =
          fastapi.Depends(deps.get_auth_service),
  ) -> user_schemas.TokenResponse:
      """Аутентификация, возврат JWT-токена."""
      token = await auth_service.authenticate(credentials)
      if not token:
          raise fastapi.HTTPException(
              status_code=http_status.HTTP_401_UNAUTHORIZED,
              detail="Invalid credentials",
          )
      return token
  ```,
  caption: [Реализация REST-эндпоинтов аутентификации],
) <auth-endpoint-example>

Каждый эндпоинт использует Dependency Injection для получения экземпляра сервиса, что обеспечивает тестируемость и слабую связанность.

== Реализация сервисного слоя

Сервисный слой (Service Layer) содержит бизнес-логику приложения. Каждый сервис реализует определённый сценарий использования (use case) и использует репозитории для доступа к данным. Сервисы не имеют прямых зависимостей от HTTP-контекста или FastAPI, что позволяет тестировать их изолированно.

Пример реализации сервиса аутентификации представлен в листинге @auth-service-example. Сервис инкапсулирует логику регистрации, проверки существования email, хеширования пароля и создания JWT-токена.

#figure(
  ```python
  # app/services/auth.py
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.core import security as core_security
  from app.core import datetime_extensions as dte
  from app.domain import errors as domain_errors
  from app.repositories import user as user_repository
  from app.schemas import users as user_schemas

  class AuthService:
      """Сервис аутентификации и управления пользователями."""

      def __init__(self, db: AsyncSession):
          self.db = db
          self.user_repo = user_repository.UserRepository(db)
          self.login_repo = user_repository.LoginDataRepository(db)

      async def register_user(
          self, user_data: user_schemas.UserCreate
      ) -> user_schemas.UserResponse:
          """Регистрация нового пользователя."""
          existing = await self.user_repo.get_by_email(user_data.email)
          if existing:
              raise domain_errors.BadRequestError(
                  "Email already registered"
              )

          # Создание пользователя и login_data
          user = await self.user_repo.create({...})
          hashed = core_security.get_password_hash(user_data.password)
          await self.login_repo.create({
              "user_id": user.id,
              "password_hash": hashed,
          })
          return user_schemas.UserResponse.model_validate(user)

      async def authenticate(
          self, credentials: user_schemas.LoginRequest
      ) -> user_schemas.TokenResponse | None:
          """Аутентификация по email/username и паролю."""
          user = await self.user_repo.get_by_email_or_username(
              credentials.username_or_email
          )
          if not user:
              return None
          login_data = await self.login_repo.get_by_user_id(user.id)
          if not login_data:
              return None
          if not core_security.verify_password(
              credentials.password, login_data.password_hash
          ):
              return None
          # Генерация JWT
          token = core_security.create_access_token({
              "sub": str(user.id),
              "role": user.role,
          })
          return user_schemas.TokenResponse(
              access_token=token,
              token_type="bearer",
              user=user_schemas.UserResponse.model_validate(user),
          )
  ```,
  caption: [Реализация сервиса аутентификации],
) <auth-service-example>

Данный пример демонстрирует ключевые принципы Clean Architecture в сервисном слое: сервис не импортирует ничего из FastAPI, использует репозитории для доступа к данным и возвращает DTO (UserResponse, TokenResponse).

== Реализация слоя репозиториев

Слой репозиториев реализует паттерн Repository, изолируя логику SQL-запросов от сервисного слоя. Базовый репозиторий предоставляет общие CRUD-операции, а специализированные репозитории расширяют его доменными методами.

#figure(
  ```python
  # app/repositories/base.py
  import typing as tp
  import sqlalchemy as sa
  from sqlalchemy.ext import asyncio as sa_asyncio
  from app.db import session as db_session

  T = tp.TypeVar("T", bound=db_session.Base)

  class BaseRepository(tp.Generic[T]):
      """Базовый репозиторий с CRUD-операциями."""

      def __init__(self, model: type[T], db: sa_asyncio.AsyncSession):
          self.model = model
          self.db = db

      async def get_by_id(self, id: int) -> T | None:
          stmt = sa.select(self.model).where(
              self.model.id == id
          )
          result = await self.db.execute(stmt)
          return result.scalar_one_or_none()

      async def create(self, obj_in: dict[str, tp.Any]) -> T:
          db_obj = self.model(**obj_in)
          self.db.add(db_obj)
          await self.db.commit()
          await self.db.refresh(db_obj)
          return db_obj

      async def update(
          self, id: int, obj_in: dict[str, tp.Any]
      ) -> T | None:
          db_obj = await self.get_by_id(id)
          if not db_obj:
              return None
          for field, value in obj_in.items():
              if hasattr(db_obj, field):
                  setattr(db_obj, field, value)
          await self.db.commit()
          await self.db.refresh(db_obj)
          return db_obj
  ```,
  caption: [Реализация базового репозитория],
) <base-repository-example>

Базовый репозиторий параметризован типом модели (tp.Generic[T]), что обеспечивает типобезопасность при создании специализированных репозиториев. Пример специализированного репозитория пользователя приведён в листинге @user-repository-example.

#figure(
  ```python
  # app/repositories/user.py
  from app.repositories.base import BaseRepository
  from app.models.users import User, LoginData

  class UserRepository(BaseRepository[User]):
      """Репозиторий для работы с пользователями."""

      def __init__(self, db):
          super().__init__(User, db)

      async def get_by_email(self, email: str) -> User | None:
          import sqlalchemy as sa
          stmt = sa.select(User).where(User.email == email)
          result = await self.db.execute(stmt)
          return result.scalar_one_or_none()

      async def get_by_email_or_username(
          self, login: str
      ) -> User | None:
          import sqlalchemy as sa
          stmt = sa.select(User).where(
              sa.or_(User.email == login, User.username == login)
          )
          result = await self.db.execute(stmt)
          return result.scalar_one_or_none()
  ```,
  caption: [Специализированный репозиторий пользователя],
) <user-repository-example>

== Реализация слоя безопасности

Безопасность серверной части реализована на двух уровнях: хеширование паролей с использованием алгоритма Argon2id и аутентификация через JSON Web Token (JWT).

Argon2id является современным стандартом хеширования паролей, устойчивым к атакам с использованием GPU и ASIC. Данный алгоритм рекомендован в качестве основного для защиты учётных данных веб-приложений @hoffman2021. Реализация хеширования приведена в листинге @security-example.

#figure(
  ```python
  # app/core/security.py
  import argon2
  import jose.jwt as jose_jwt
  from app.core import config as core_config
  from app.core import datetime_extensions as dte

  # Argon2id с рекомендуемыми параметрами
  ph = argon2.PasswordHasher(
      time_cost=2,        # Количество итераций
      memory_cost=65536,  # Память 64 MB
      parallelism=1,      # Потоков
      hash_len=32,        # Длина хеша
      salt_len=16,        # Длина соли
  )

  def verify_password(plain_password: str, hashed_password: str) -> bool:
      """Верификация пароля через Argon2id."""
      try:
          ph.verify(hashed_password, plain_password)
          return True
      except argon2.exceptions.VerifyMismatchError:
          return False

  def create_access_token(data: dict) -> str:
      """Создание JWT-токена с expiration."""
      to_encode = data.copy()
      expire = dte.now_utc() + core_config.settings.ACCESS_TOKEN_EXPIRE
      to_encode.update({"exp": expire})
      return jose_jwt.encode(
          to_encode,
          core_config.settings.SECRET_KEY,
          algorithm=core_config.settings.ALGORITHM,
      )
  ```,
  caption: [Реализация безопасности: Argon2id + JWT],
) <security-example>

== Конфигурация и запуск приложения

Конфигурация приложения осуществляется через переменные окружения с использованием библиотеки pydantic-settings. Основные параметры включают подключение к базе данных, настройки CORS, секретный ключ для JWT и параметры Redis (опционально, для realtime-чата).

#figure(
  ```python
  # app/core/config.py
  from pydantic_settings import BaseSettings

  class Settings(BaseSettings):
      APP_NAME: str = "Web Education Platform API"
      APP_VERSION: str = "1.0.0"
      DEBUG: bool = True
      API_V1_PREFIX: str = "/api/v1"
      DATABASE_URL: str = "postgresql://..."
      REDIS_URL: str | None = None  # Опционально
      SECRET_KEY: str = "change-me"
      ALGORITHM: str = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
      BACKEND_CORS_ORIGINS: list[str] = [
          "http://localhost:5173"
      ]

      model_config = {"env_file": ".env"}

  settings = Settings()
  ```,
  caption: [Конфигурация приложения через pydantic-settings],
) <config-example>

Точка входа приложения (листинг @main-entrypoint) инициализирует FastAPI, подключает middleware (CORS, RequestIdMiddleware), регистрирует обработчики доменных ошибок и монтирует API-роутер с префиксом /api/v1.

#figure(
  ```python
  # app/main.py (ключевые элементы)
  import fastapi
  from fastapi.middleware import cors as fastapi_cors
  from app.api import errors as api_errors
  from app.api import openapi as api_openapi
  from app.api.middleware import request_id as request_id_middleware
  from app.api import v1 as api_v1
  from app.core import config as core_config

  app = fastapi.FastAPI(
      title=core_config.settings.APP_NAME,
      version=core_config.settings.APP_VERSION,
      debug=core_config.settings.DEBUG,
      docs_url="/api/docs",
      openapi_url="/api/openapi.json",
  )

  app.add_middleware(fastapi_cors.CORSMiddleware, ...)
  app.add_middleware(request_id_middleware.RequestIdMiddleware)
  api_errors.register_exception_handlers(app)
  api_openapi.install_openapi_patch(app)
  app.include_router(
      api_v1.api_router,
      prefix=core_config.settings.API_V1_PREFIX,
  )
  ```,
  caption: [Точка входа приложения FastAPI],
) <main-entrypoint>

== Интеграция с realtime-чатом

В дополнение к REST API серверная часть включает поддержку WebSocket-чата для обмена сообщениями в реальном времени. Механизм realtime-чата реализован с использованием Connection Manager и опционального Redis Pub/Sub для поддержки многоэкземплярного развёртывания:

```python
# app/main.py (startup)
from app.realtime import connection_manager as cm
from app.realtime import redis_pubsub as rp

@app.on_event("startup")
async def on_startup():
    app.state.chat_connection_manager = cm.ConnectionManager()
    if core_config.settings.REDIS_URL:
        redis_client = redis_asyncio.from_url(
            core_config.settings.REDIS_URL
        )
        app.state.chat_broker = rp.RedisPubSubBroker(
            redis_client,
            manager=app.state.chat_connection_manager,
        )
```

Redis является опциональным компонентом: если REDIS_URL не задан, приложение работает без realtime-функций, что упрощает локальную разработку.

== Выводы по главе

В данной главе описана реализация серверной части системы управления обучением на основе спроектированной Clean Architecture. Разработан REST API на FastAPI, включающий эндпоинты для аутентификации, управления классами, уроками, домашними заданиями, тестированием и чатом. Каждый эндпоинт следует принципу разделения ответственности, делегируя бизнес-логику сервисам.

Реализован сервисный слой с примерами аутентификации и управления пользователями. Сервисы не зависят от HTTP-контекста и могут тестироваться изолированно. Слой репозиториев, основанный на базовом CRUD-репозитории, изолирует SQL-запросы от бизнес-логики.

Обеспечена безопасность приложения: хеширование паролей через Argon2id и аутентификация через JWT. Реализована конфигурация через переменные окружения (pydantic-settings) и опциональная поддержка realtime-чата через Redis Pub/Sub.

Разработанная серверная часть обеспечивает полный цикл операций, необходимых для функционирования системы управления обучением, и полностью соответствует принципам Clean Architecture.
