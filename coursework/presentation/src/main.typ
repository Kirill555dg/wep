#import "@preview/touying:0.7.3": *
#import themes.university: *
#import "../../const.typ"

#let assets = "../../assets/"
#let logo = "logo.png"
#let primary = rgb("#000000")
#let muted = rgb("#333333")
#let border = rgb("#a5a5a5")
#let light = rgb("#f7f7f7")

#show: university-theme.with(
  aspect-ratio: "16-9",
  progress-bar: false,
  header: none,
  footer-columns: (1fr, 1fr, auto),
  footer-a: none,
  footer-b: none,
  footer-c: none,
  config-common(slide-level: 2),
  config-colors(
    primary: primary,
    secondary: primary,
    tertiary: primary,
    neutral-lightest: rgb("#ffffff"),
    neutral-darkest: primary,
  ),
  config-info(
    title: [Серверная часть веб-приложения для управления образовательными курсами],
    subtitle: [Курсовая работа по дисциплине «Бэкенд-разработка»],
    author: [Миркин Кирилл Леонидович],
    date: [Москва 2026],
    institution: [РТУ МИРЭА, ИИТ, ИиППО],
    logo: none,
  ),
)

#set text(font: "Times New Roman", size: 20pt, fill: primary)
#set block(above: auto, below: const.leading-one)
#set par(leading: const.leading-one, spacing: const.leading-one)
#set heading(numbering: none)
#show heading: set par(justify: false, leading: const.leading-one)
#show heading: set block(above: auto, below: const.leading-one)
#show list: it => {
  for child in it.children {
    let marker = "–"
    par[#marker#h(const.leading-one)#child.body]
  }
}
#show table: it => {
  set block(breakable: false)
  show table.cell: cell => {
    set align(if cell.y == 0 { center + horizon } else { left + top })
    cell
  }
  it
}
#set table(stroke: const.stroke)
#show figure: it => {
  show figure.caption: set text(size: 14pt)
  set par(justify: false, leading: const.leading-one)
  block(breakable: false, below: const.leading-one, { it })
}
#show figure.where(kind: raw): it => {
  block(breakable: false, below: const.leading-one, {
    align(left, it.caption)
    set text(size: 14pt)
    table(
      columns: (1fr,),
      stroke: const.stroke,
      align: left,
      it.body,
    )
  })
}

#let slide-title(body) = [
  #text(36pt, weight: "bold")[#body]
]
#let note(body) = text(14pt, fill: muted)[#body]
#let fig(path, width: 88%) = align(center)[#image(path, width: width)]
#let code-box(body) = rect(width: 100%, inset: 8pt, fill: light, stroke: border, radius: 2pt)[#body]

#slide[
  #align(center + top)[
    #set text(size: 14pt)
    #image("title.png", width: 50%)

    #text(weight: "bold")[КУРСОВАЯ РАБОТА]

    #align(left)[по дисциплине: Бэкенд-разработка]
    #align(left)[по профилю: Разработка программных продуктов и проектирование информационных систем]
    #align(left)[направления подготовки: 09.03.04 «Программная инженерия»]
    #v(0.5cm)
    #align(left)[Тема: Серверная часть веб-приложения для управления образовательными курсами]
    #v(0.5cm)
    #align(left)[Студент: Миркин Кириль Леонидович]
    #align(left)[Группа: ИКБО-10-23]
    #align(left)[Руководитель: Волков Михаил Юрьевич, ст. преподаватель]
    #v(0.5cm)
    Москва 2026
  ]
]


#show: university-theme.with(
  aspect-ratio: "16-9",
  progress-bar: false,
  header: none,
  header-right: self => [
    #image(logo, height: 2cm)
  ],
  footer-columns: (1fr, 1fr, auto),
  footer-a: none,
  footer-b: none,
  footer-c: self => [
    #text(14pt, fill: primary)[
      #pad(right: 0.5cm, bottom: 2cm)[
        #align(right)[
          #context utils.slide-counter.display()
        ]
      ]
    ]
  ],
  config-common(slide-level: 2),
  config-colors(
    primary: primary,
    secondary: primary,
    tertiary: primary,
    neutral-lightest: rgb("#ffffff"),
    neutral-darkest: primary,
  ),
  config-info(
    title: [Серверная часть веб-приложения для управления образовательными курсами],
    subtitle: [Курсовая работа по дисциплине «Бэкенд-разработка»],
    author: [Миркин Кирилл Леонидович],
    date: [Москва 2026],
    institution: [РТУ МИРЭА, ИИТ, ИиППО],
    logo: none,
  ),
)


#set text(font: "Times New Roman", size: 20pt, fill: primary)
#set block(above: auto, below: const.leading-one)
#set par(leading: const.leading-one, spacing: const.leading-one)
#set heading(numbering: none)
#show heading: set par(justify: false, leading: const.leading-one)
#show heading: set block(above: auto, below: const.leading-one)
#show list: it => {
  for child in it.children {
    let marker = "–"
    par[#marker#h(const.leading-one)#child.body]
  }
}
#show table: it => {
  set block(breakable: false)
  show table.cell: cell => {
    set align(if cell.y == 0 { center + horizon } else { left + top })
    cell
  }
  it
}
#set table(stroke: const.stroke)
#show figure: it => {
  show figure.caption: set text(size: 14pt)
  set par(justify: false, leading: const.leading-one)
  block(breakable: false, below: const.leading-one, { it })
}
#show figure.where(kind: raw): it => {
  block(breakable: false, below: const.leading-one, {
    align(left, it.caption)
    set text(size: 14pt)
    table(
      columns: (1fr,),
      stroke: const.stroke,
      align: left,
      it.body,
    )
  })
}

== Цель и задачи работы
#slide[
  #slide-title[Цель и задачи работы]
  #list(
    [Цель работы – разработка серверной части LMS-системы на основе Clean Architecture.],
    [Провести анализ предметной области и существующих LMS-решений.],
    [Обосновать выбор архитектурного подхода и технологического стека.],
    [Разработать архитектуру серверной части и структуру базы данных.],
    [Реализовать REST API, механизмы безопасности и автоматической проверки ответов.],
    [Показать взаимодействие серверной и клиентской частей системы.],
  )
]

== Предметная область и требования
#slide[
  #slide-title[Предметная область и требования]
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.9cm,
    [
      #text(weight: "bold")[Предметная область]
      #list(
        [учебные классы, уроки и теоретические материалы],
        [домашние задания и переиспользуемая база задач],
        [тестирование, оценивание и статистика],
        [взаимодействие преподавателя и студента через чат],
      )
    ],
    [
      #text(weight: "bold")[Ключевые требования]
      #list(
        [REST API для клиентского приложения],
        [Clean Architecture и слабая связанность слоёв],
        [PostgreSQL как основная СУБД],
        [межстраничная навигация и современный интерфейс],
      )
    ],
  )
]

== Анализ аналогов LMS-систем
#slide[
  #slide-title[Анализ аналогов LMS-систем]
  #v(0.35cm)
  #table(
    columns: (1.35fr, 1.45fr, 1.45fr, 1.45fr, 1.45fr),
    table.header([Критерий], [Moodle], [Google Classroom], [Stepik], [Фоксфорд]),
    [Сильная сторона],
    [гибкость и зрелое тестирование],
    [простота запуска],
    [мощная автопроверка],
    [близость к школьной модели],

    [Ограничение],
    [сложность сопровождения],
    [нет автопроверки и собственного сервера],
    [нет модели закрытого класса],
    [нет открытого API],

    [Вывод для проекта], [частичная база задач], [код класса], [автоматическая проверка], [уроки, ДЗ, чат],
  )
]

== Выбор архитектурного подхода
#slide[
  #slide-title[Выбор архитектурного подхода]
  #list(
    [DDD обеспечивает глубокое моделирование предметной области, но избыточен для текущего объёма системы.],
    [MVC/MVT удобен на старте, однако затрудняет изоляцию бизнес-логики от фреймворка.],
    [Clean Architecture обеспечивает явное разделение слоёв, независимость бизнес-правил и высокую тестируемость.],
  )
]

== Технологический стек
#slide[
  #slide-title[Технологический стек]
  #grid(
    columns: auto,
    gutter: 0.7cm,
    [
      #list(
        [Python 3.12+ – актуальная версия языка с высокой производительностью и улучшенной поддержкой типизации.],
        [FastAPI – современный асинхронный фреймворк с Dependency Injection и OpenAPI.],
        [PostgreSQL – надёжная ACID-СУБД для прикладных систем среднего масштаба.],
        [SQLAlchemy 2.0 + Alembic – ORM и миграции, не зависящие от конкретного веб-фреймворка.],
        [React + TypeScript – клиентская часть, потребляющая REST API.],
      )
    ],
    [
      #fig(assets + "fastapi-popularity.png", width: 100%)
    ],
  )
]

== Архитектура серверной части
#slide[
  #slide-title[Архитектура серверной части]

  Система организована по принципам Clean Architecture: HTTP-слой делегирует выполнение сервисам, сервисы обращаются к репозиториям, а доступ к данным инкапсулирован на уровне ORM-моделей и PostgreSQL.
  #fig(assets + "components-diagram.png", width: 50%)
]

== Структура базы данных
#slide[
  #slide-title[Структура базы данных]

  Ключевые сущности: users, login_data, classrooms, lessons, homework, problems, statistics, chat и message. Схема поддерживает разделение ролей, переиспользуемую базу задач и хранение истории взаимодействия.
  #fig(assets + "er-diagram.png", width: 60%)
]

== REST API и OpenAPI-контракт
#slide[
  #slide-title[REST API и OpenAPI-контракт]
  #grid(
    columns: 1fr,
    gutter: 0.8cm,
    [
      #list(
        [группы эндпоинтов: auth, classrooms, lessons, homework, problems, testing, statistics, theory],
        [единый префикс `/api/v1`],
        [автоматическая генерация OpenAPI-спецификации],
        [единый контракт для backend и frontend],
      )
    ],
    [

      #fig(assets + "openapi-scheme.png", width: 75%)
      OpenAPI-документация используется как машинно-читаемое описание интерфейса серверной части.
    ],
  )
]

== Безопасность серверной части
#slide[
  #slide-title[Безопасность серверной части]
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.8cm,
    [
      #list(
        [Argon2id используется для хеширования паролей.],
        [JWT применяется для безсессионной аутентификации.],
        [роль пользователя проверяется при доступе к защищённым ресурсам.],
        [ошибки обработки запросов возвращаются в унифицированном формате.],
      )
    ],
    [
      #code-box[
        #raw(
          block: true,
          lang: "python",
          "_MEMORY_COST_KIB = 1024 * 64\nph = argon2.PasswordHasher(\n    time_cost=2,\n    memory_cost=_MEMORY_COST_KIB,\n    parallelism=1,\n)\n\ndef create_access_token(data: dict) -> str:\n    payload = {**data, \"exp\": utc_now() + ttl}\n    return jose_jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)",
        )
      ]
    ],
  )
]

== Ключевой сценарий: автоматическая проверка ответа
#slide[
  #slide-title[Ключевой сценарий: автоматическая проверка ответа]
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.8cm,
    [
      #list(
        [проверка прав доступа студента],
        [проверка существования задания и задачи],
        [поиск задачи в составе домашнего задания],
        [сравнение ответа с эталоном],
        [обновление балла, числа попыток и времени],
      )
    ],
    [
      #code-box[
        #raw(
          block: true,
          lang: "python",
          "async def submit_answer(...):\n    stats = await self.stats_repo.get_or_create_stats(...)\n    is_correct = self._check_answer(answer, correct_answer)\n    new_score = min(stats.score + points, stats.max_score)\n    updated = await self.stats_repo.update(stats.id, {...})\n    return StatisticsResponse.model_validate(updated)",
        )
      ]
    ],
  )
]

== Тестирование серверной части
#slide[
  #slide-title[Тестирование серверной части]
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.8cm,
    [
      #list(
        [pytest используется для автоматизированной проверки бизнес-логики],
        [каждый тест выполняется в отдельной схеме PostgreSQL],
        [проверяются AuthService, ChatService, ProblemService, ResultService, TheoryService и realtime-модули],
        [изолированное тестирование подтверждает корректность Clean Architecture],
      )
    ],
    [
      #fig(assets + "backend-tests.png", width: 100%)
    ],
  )
]

== Клиентское представление и интеграция
#slide[
  #slide-title[Клиентское представление и интеграция]
  #grid(
    columns: (1fr, 1fr),
    gutter: 0.6cm,
    [
      #fig(assets + "teacher-main-page-ui.png", width: 100%)
    ],
    [
      #fig(assets + "student-homework-page-ui.png", width: 93%)
    ],

    [
      #note[Интерфейс преподавателя: работа с классом, учениками и кодом приглашения.]
    ],
    [
      #note[Интерфейс студента: выполнение домашнего задания и отправка ответа.]

    ],
  )
  #v(0.3cm)
  Frontend реализован на React + TypeScript по методологии Feature-Sliced Design и взаимодействует с сервером через OpenAPI-контракт и axios-клиент.
]

== Основные результаты работы
#slide[
  #slide-title[Основные результаты работы]
  #list(
    [Проведён анализ предметной области и LMS-аналогов.],
    [Обоснован выбор Clean Architecture и технологического стека.],
    [Разработана архитектура серверной части и схема базы данных.],
    [Реализованы REST API, аутентификация, автопроверка, статистика и чат.],
    [Подготовлена клиентская часть как потребитель REST API.],
    [Корректность решений подтверждена автоматизированным тестированием.],
  )
]

= Спасибо за внимание!
