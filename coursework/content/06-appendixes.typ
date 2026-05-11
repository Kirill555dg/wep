#import "@preview/modern-g7-32:0.2.0": appendixes

#show: appendixes

= Фрагменты исходного кода серверной части

== Слой репозиториев

#figure(
  ```python
  # app/repositories/base.py
  T = TypeVar("T", bound=Base)

  class BaseRepository(Generic[T]):
      """Базовый репозиторий с CRUD-операциями."""

      def __init__(self, model: Type[T], db: AsyncSession):
          self.model = model
          self.db = db

      async def get_by_id(self, id: int) -> T | None:
          stmt = select(self.model).where(self.model.id == id)
          result = await self.db.execute(stmt)
          return result.scalar_one_or_none()

      async def create(self, obj_in: dict[str, Any]) -> T:
          db_obj = self.model(**obj_in)
          self.db.add(db_obj)
          await self.db.commit()
          await self.db.refresh(db_obj)
          return db_obj

      async def update(self, id: int, obj_in: dict[str, Any]) -> T | None:
          db_obj = await self.get_by_id(id)
          if not db_obj: return None
          for field, value in obj_in.items():
              if hasattr(db_obj, field):
                  setattr(db_obj, field, value)
          await self.db.commit()
          await self.db.refresh(db_obj)
          return db_obj

      async def delete(self, id: int) -> bool:
          db_obj = await self.get_by_id(id)
          if not db_obj: return False
          await self.db.delete(db_obj)
          await self.db.commit()
          return True
  ```,
  caption: [Базовый репозиторий с CRUD-операциями],
) <base-repository-appendix>

== Конфигурация приложения

#figure(
  ```python
  # app/core/config.py
  class Settings(BaseSettings):
      APP_NAME: str = "Web Education Platform API"
      APP_VERSION: str = "1.0.0"
      DEBUG: bool = True
      API_V1_PREFIX: str = "/api/v1"

      DATABASE_URL: str = (
          "postgresql://wep_user:wep_password@127.0.0.1:5432/wep_education"
      )
      BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]
      BACKEND_CORS_ALLOW_CREDENTIALS: bool = True
      BACKEND_CORS_ALLOW_METHODS: list[str] = ["*"]
      BACKEND_CORS_ALLOW_HEADERS: list[str] = [
          "Authorization", "Content-Type", "X-Request-ID",
      ]

      SECRET_KEY: str = "change-in-production"
      ALGORITHM: str = "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

      REDIS_URL: str | None = None  # опционально, включает WebSocket-чат

      model_config = SettingsConfigDict(
          env_file=".env", case_sensitive=True, extra="ignore",
      )

  settings = Settings()
  ```,
  caption: [Конфигурация приложения через pydantic-settings],
) <config-appendix>

== Точка входа приложения

#figure(
  ```python
  # app/main.py
  app = fastapi.FastAPI(
      title=settings.APP_NAME,
      docs_url="/api/docs",
      openapi_url="/api/openapi.json",
  )

  app.add_middleware(CORSMiddleware,
      allow_origins=settings.BACKEND_CORS_ORIGINS,
      allow_credentials=settings.BACKEND_CORS_ALLOW_CREDENTIALS,
      allow_methods=settings.BACKEND_CORS_ALLOW_METHODS,
      allow_headers=settings.BACKEND_CORS_ALLOW_HEADERS,
  )
  app.add_middleware(RequestIdMiddleware)

  api_errors.register_exception_handlers(app)
  api_openapi.install_openapi_patch(app)

  app.include_router(api_v1.api_router,
                     prefix=settings.API_V1_PREFIX)

  @app.on_event("startup")
  async def on_startup() -> None:
      app.state.chat_connection_manager = ConnectionManager()
      app.state.chat_broker = None
      if settings.REDIS_URL:
          redis = redis_asyncio.from_url(settings.REDIS_URL)
          await redis.ping()
          app.state.chat_broker = RedisPubSubBroker(
              redis, manager=app.state.chat_connection_manager,
          )
  ```,
  caption: [Точка входа приложения FastAPI],
) <main-appendix>

== Производная URL подключения к СУБД

#figure(
  ```python
  # app/db/url.py
  def normalize_postgres_url(url: str, *, drivername: str) -> str:
      parsed = make_url(url)
      if parsed.get_backend_name() != "postgresql":
          return parsed.render_as_string(hide_password=False)
      parsed = parsed.set(drivername=drivername)
      if drivername == "postgresql+asyncpg":
          query = dict(parsed.query)
          query.pop("gssencmode", None)
          parsed = parsed.set(query=query)
      return parsed.render_as_string(hide_password=False)

  def to_psycopg_url(url: str) -> str:
      return normalize_postgres_url(url, drivername="postgresql+psycopg")

  def to_asyncpg_url(url: str) -> str:
      return normalize_postgres_url(url, drivername="postgresql+asyncpg")
  ```,
  caption: [Централизованное вычисление URL драйвера PostgreSQL],
) <db-url-appendix>
