#import "../const.typ"

#let terms-table(body) = {
  let items = body.children.filter(it => it.func() == terms.item)

  let get-text(content) = {
    if content.has("children") and content.children.len() > 0 {
      let first = content.children.at(0)
      if first.has("text") { return first.text }
    }
    if content.has("text") { return content.text }
    ""
  }

  let sorted = items.sorted(key: it => lower(get-text(it.term)))
  let rows = sorted.map(it => (it.term, [–#h(const.leading-one)#it.description]))

  set par(justify: true)

  table(
    columns: (1fr, 2fr),
    align: left + top,
    stroke: none,
    inset: 0mm,
    column-gutter: const.leading-one,
    row-gutter: const.leading-one-and-a-half,
    ..rows.flatten()
  )
}

#[
  #show heading: it => align(center, upper(it))
  #heading(numbering: none)[Определения, обозначения и сокращения]
]

В настоящем отчёте применяют следующие определения, обозначения и сокращения.

#terms-table[
  / API (Application Programming Interface): программный интерфейс, определяющий способы взаимодействия компонентов программного обеспечения.
  / Argon2: алгоритм хеширования паролей, устойчивый к атакам с использованием GPU и ASIC.
  / Clean Architecture: архитектурный паттерн, предложенный Робертом Мартином, обеспечивающий независимость бизнес-логики от фреймворков, баз данных и внешних интерфейсов.
  / DDD (Domain-Driven Design): подход к проектированию программного обеспечения, ориентированный на моделирование предметной области и использование единого языка (Ubiquitous Language).
  / Dependency Injection (DI): паттерн проектирования, при котором зависимости компонентов передаются извне, а не создаются внутри компонента.
  / DTO (Data Transfer Object): объект передачи данных, используемый для обмена структурированной информацией между слоями приложения.
  / ER-диаграмма (Entity-Relationship Diagram): диаграмма «сущность–связь», используемая для моделирования структуры данных и отношений между сущностями.
  / FastAPI: современный веб-фреймворк для Python, ориентированный на создание REST API с поддержкой асинхронности, автоматической валидации данных и документирования.
  / HTTP (HyperText Transfer Protocol): протокол передачи данных между клиентом и сервером в веб-среде.
  / JWT (JSON Web Token): компактный и самодостаточный формат для передачи данных в виде JSON-объекта, используемый для аутентификации.
  / LMS (Learning Management System): система управления обучением, предназначенная для организации образовательного процесса, хранения материалов и контроля результатов.
  / MVC (Model-View-Controller): архитектурный паттерн, разделяющий приложение на три взаимосвязанных компонента: модель, представление и контроллер.
  / ORM (Object-Relational Mapping): технология отображения объектных структур в реляционные базы данных.
  / REST (Representational State Transfer): архитектурный стиль взаимодействия распределённых систем, использующий принципы унифицированного интерфейса и обмена представлениями ресурсов.
  / SQL (Structured Query Language): язык запросов, используемый для управления реляционными базами данных.
  / SQLAlchemy: библиотека ORM и инструмент работы с реляционными базами данных в Python.
  / Repository: паттерн, инкапсулирующий логику доступа к данным и предоставляющий интерфейс для операций с сущностями.
  / Service Layer: слой бизнес-логики приложения, обрабатывающий прикладные операции и обращающийся к репозиториям.
  / СУБД: система управления базами данных.
  / Фреймворк: программный каркас, упрощающий разработку приложений и задающий архитектурные принципы.
]
