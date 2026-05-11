#import "../../const.typ"

= Разработка серверной части интернет-ресурса

== Реализация REST API на FastAPI

Серверная часть реализована на Python (версия 3.12+) с использованием FastAPI @fastapi-docs @eliseev2024. Все маршруты сгруппированы по функциональным областям и зарегистрированы единым корневым роутером в `app/api/v1/__init__.py`:

```
/api/v1/auth/       – аутентификация и управление ролями
/api/v1/classrooms/ – классы, приглашения, чат, WebSocket
/api/v1/lessons/    – уроки
/api/v1/homework/   – домашние задания
/api/v1/problems/   – база задач
/api/v1/testing/    – приём ответов, автопроверка
/api/v1/statistics/ – прогресс и статистика
/api/v1/theory/     – теоретические материалы
```

При проектировании API соблюдаются стандартные принципы REST @alpatov2024. Взаимодействие строится вокруг ресурсов, доступ к которым осуществляется через стандартные HTTP-методы (GET, POST, PATCH, DELETE). Принцип взаимодействия между клиентом и сервером посредством REST API проиллюстрирован на рисунке @rest-api-principle.

#figure(
  image("../../assets/rest-api-principle.png", width: 85%),
  caption: [Принцип взаимодействия через REST API],
) <rest-api-principle>

Каждый обработчик выполняет единственную задачу: валидирует входные данные через Pydantic-схему, вызывает сервис и транслирует результат в HTTP-ответ. Пример эндпоинта аутентификации приведён в листинге @auth-endpoint-example.

#figure(
  ```python
  # app/api/v1/auth.py
  @router.post("/login", response_model=TokenResponse)
  async def login(
      credentials: LoginRequest,
      auth_service: AuthService = Depends(deps.get_auth_service),
  ) -> TokenResponse:
      try:
          token = await auth_service.authenticate(credentials)
      except ServiceError as exc:
          if exc.code == "inactive_user":
              raise http_errors.forbidden(exc.message, code=exc.code)
          raise
      if token is None:
          raise http_errors.unauthorized("Invalid username/email or password")
      return token
  ```,
  caption: [Реализация эндпоинта аутентификации],
) <auth-endpoint-example>

Листинг демонстрирует принцип явной обработки ошибок: обработчик знает семантику каждого кода и выбирает HTTP-статус самостоятельно. Незнакомое исключение не перехватывается – ответ 500 сигнализирует об ошибке на стороне сервера.

== Реализация сервисного слоя

Сервисный слой реализует бизнес-сценарии и не зависит от HTTP-контекста. Сервисы используют репозитории для доступа к данным. В листинге @auth-service-example показан сервис аутентификации.

#figure(
  ```python
  # app/services/auth.py
  class AuthService:
      def __init__(self, db: AsyncSession):
          self.user_repo  = UserRepository(db)
          self.login_repo = LoginDataRepository(db)
          self.teacher_repo = TeacherRepository(db)
          self.student_repo = StudentRepository(db)

      async def register_user(self, data: UserCreate) -> UserResponse:
          if await self.user_repo.get_by_email(data.email):
              raise ServiceError("Email already registered", code="email_taken")
          user = await self.user_repo.create({
              "username": data.username or data.email.split("@")[0],
              "email": data.email, "first_name": data.first_name,
              "last_name": data.last_name, "role": data.role.value,
              "is_active": True, ...
          })
          hashed = security.get_password_hash(data.password)
          await self.login_repo.create_for_user(user.id, hashed)
          # профиль роли создаётся только для активной роли
          if user.role == "teacher":
              await self.teacher_repo.create({"user_id": user.id})
          else:
              await self.student_repo.create({"user_id": user.id})
          return UserResponse.model_validate(user)

      async def authenticate(
          self, login: LoginRequest,
      ) -> TokenResponse | None:
          user = await self.user_repo.get_by_username_or_email(
              login.username_or_email
          )
          if not user: return None
          if not user.is_active:
              raise ServiceError("User account is inactive", code="inactive_user")
          info = await self.login_repo.get_by_user_id(user.id)
          if not info or not security.verify_password(login.password, info.hashed_password):
              return None
          token = security.create_access_token({"sub": str(user.id), "role": user.role})
          return TokenResponse(access_token=token,
                               user=UserResponse.model_validate(user))
  ```,
  caption: [Реализация сервиса аутентификации],
) <auth-service-example>

Сервис TestingService реализует ключевой сценарий автоматической проверки ответов студента. Код соответствующего фрагмента приведён в листинге @testing-service-example.

#figure(
  ```python
  # app/services/testing.py — фрагмент метода submit_answer
  async def submit_answer(
      self, answer_data: AnswerSubmit, student_user_id: int,
  ) -> StatisticsResponse:
      # ... [Проверка прав доступа, существования задачи и её принадлежности к ДЗ] ...

      stats = await self.stats_repo.get_or_create_stats(
          student.id, answer_data.homework_id, homework.max_score,
      )
      
      # Автоматическая проверка ответа студента
      is_correct = self._check_answer(answer_data.answer, problem.correct_answer)
      
      # Начисление баллов с ограничением по максимальному баллу
      new_score = (
          min(stats.score + hw_problem.points, stats.max_score) if is_correct
          else stats.score
      )
      
      # Фиксация попытки и затраченного времени
      updated = await self.stats_repo.update(stats.id, {
          "score": new_score, "status": "in_progress",
          "attempts_count": stats.attempts_count + 1,
          "time_spent_minutes": stats.time_spent_minutes + answer_data.time_spent_minutes,
      })
      return StatisticsResponse.model_validate(updated)

  def _check_answer(self, student: str, correct: str | None) -> bool:
      if not correct: return False
      return student.strip().lower() == correct.strip().lower()
  ```,
  caption: [Фрагмент реализации автоматической проверки ответа],
) <testing-service-example>

== Слой безопасности

Безопасность реализована на двух уровнях: хеширование паролей и аутентификация через JWT.

Пароли хешируются алгоритмом Argon2id – устойчивым к атакам с использованием GPU и ASIC, рекомендованным для хранения учётных данных @hoffman2021. JWT-токены формируются с кратким сроком действия и содержат идентификатор пользователя и активную роль, что позволяет обнаруживать смену роли без обращения к базе данных.

#figure(
  ```python
  # app/core/security.py
  _MEMORY_COST_KIB = 1024 * 64  # 64 MB

  ph = argon2.PasswordHasher(
      time_cost=2, memory_cost=_MEMORY_COST_KIB,
      parallelism=1, hash_len=32, salt_len=16,
  )

  def verify_password(plain: str, hashed: str) -> bool:
      try:
          ph.verify(hashed, plain)
          return True
      except argon2.exceptions.VerifyMismatchError:
          return False

  def create_access_token(data: dict) -> str:
      payload = {**data, "exp": utc_now() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
      return jose_jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
  ```,
  caption: [Реализация безопасности: Argon2id и JWT],
) <security-example>

== Управление конфигурацией и запуск

Конфигурация приложения хранится в переменных окружения, загружаемых через `pydantic-settings` @pydantic-docs. Точка входа (`app/main.py`) подключает middleware (CORS, `RequestIdMiddleware`), глобальные обработчики ошибок и API-роутер с префиксом `/api/v1`. При наличии `REDIS_URL` в момент старта инициализируется Redis Pub/Sub-брокер для многоэкземплярного WebSocket-чата; без него приложение стартует без realtime-компонента. Swagger UI доступен по адресу `/api/docs`, OpenAPI JSON – по `/api/openapi.json`. Листинги основных конфигурационных файлов и точки входа вынесены в приложение А.

== Тестируемость

Принципы Clean Architecture обеспечили практическую изоляцию сервисного слоя от веб-слоя. Тесты используют сервисы напрямую, без поднятия FastAPI. Для каждого теста создаётся отдельная схема PostgreSQL, которая накатывает таблицы из метаданных SQLAlchemy и удаляется по завершении. Это позволяет проверять бизнес-логику в реалистичных условиях при полной изоляции между тестами @sqlalchemy-docs. В наборе реализованы тесты для `AuthService`, `TestingService`, `ChatService`, `ProblemService`, `ResultService`, `TheoryService`, модулей realtime.

== Клиентское представление

Клиентская часть платформы реализована на React 18 с TypeScript @react-docs. Архитектура фронтенда построена по методологии Feature-Sliced Design (FSD) @fsd-docs, которая структурирует код в шесть слоёв по убыванию области ответственности. Принципиальная схема данной методологии представлена на рисунке @fsd-architecture.

#figure(
  image("../../assets/fsd-architecture.png", width: 80%),
  caption: [Схема слоёв методологии Feature-Sliced Design],
) <fsd-architecture>

В рамках проекта слои распределены следующим образом:

```
src/
├── app/       – инициализация, провайдеры, роутинг
├── pages/     – страницы (Login, Classrooms, Lesson, ...)
├── widgets/   – составные блоки (Header, Sidebar, ChatPanel)
├── features/  – сценарии пользователя (JoinClassroom, SubmitAnswer, ...)
├── entities/  – доменные данные (Classroom, Lesson, User, Message)
└── shared/    – переиспользуемые утилиты, UI-kit, HTTP-клиент
```

Взаимодействие с сервером ведётся через axios-клиент в `shared/api/axios.ts`. Серверный контракт описан в файле `openapi.json`, генерируемом бэкенд-командой `python -m app.scripts.export_openapi`. Управление серверным состоянием реализовано через TanStack Query v4, локальное состояние – через Zustand. Формы валидируются с помощью react-hook-form и zod. UI построен на примитивах Radix UI и стилизован через Tailwind CSS.

На рисунках @ui-classrooms, @ui-lesson и @ui-testing показан интерфейс основных страниц системы.

#figure(
  rect(width: 100%, height: 6cm, fill: luma(230))[
    #align(center + horizon)[_Скриншот: страница списка классов преподавателя_]
  ],
  caption: [Главная страница преподавателя со списком учебных классов],
) <ui-classrooms>

#figure(
  rect(width: 100%, height: 6cm, fill: luma(230))[
    #align(center + horizon)[_Скриншот: страница урока с домашним заданием_]
  ],
  caption: [Страница урока с домашним заданием для студента],
) <ui-lesson>

#figure(
  rect(width: 100%, height: 6cm, fill: luma(230))[
    #align(center + horizon)[_Скриншот: результаты тестирования_]
  ],
  caption: [Интерфейс отображения результатов автоматического тестирования],
) <ui-testing>

Связь фронтенда с бэкендом реализована через единый API-контракт OpenAPI: изменение серверного эндпоинта отражается в спецификации и может быть подхвачено кодогенерацией на стороне клиента, что обеспечивает согласованность интерфейсов без ручной синхронизации.

== Итоги разработки

Реализована серверная часть на Python с использованием FastAPI, PostgreSQL и SQLAlchemy. REST API включает девять групп эндпоинтов, покрывающих все функциональные требования системы. Обработка ошибок построена явно: сервисы возвращают `None` для lookup-операций и поднимают `ServiceError` для командных сценариев; HTTP-статус выбирает маршрутизатор. Обеспечена безопасность: Argon2id для хранения паролей и JWT для аутентификации. Тестируемость архитектуры подтверждена набором автоматизированных тестов, работающих на уровне сервисного слоя без HTTP. Реализована клиентская часть на React + TypeScript по методологии Feature-Sliced Design, потребляющая REST API через OpenAPI-контракт.
