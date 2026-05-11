describe("Страница профиля", () => {
  beforeEach(() => {
    cy.visit("/login")

    cy.get('input[name="email"]').type("teacher@school.edu")
    cy.get('input[name="password"]').type("123456")
    cy.get("button[type=submit]").click()

    cy.url().should("include", "/teacher")
    cy.visit("/profile")
  })

  it("отображает базовую информацию профиля", () => {
    cy.contains("Профиль")
    cy.contains("Смирнов") // фамилия
    cy.contains("teacher@school.edu") // email
    cy.contains("Мужской")
    cy.get("img").should("exist")
    cy.contains("О себе")
    cy.contains("Контакты")
  })

  it("отображает корректные ссылки на Telegram и VK", () => {
    cy.contains("Telegram").parent().within(() => {
      cy.get("a").should("have.attr", "href").and("include", "t.me")
    })
    cy.contains("VK").parent().within(() => {
      cy.get("a").should("have.attr", "href").and("include", "vk.com")
    })
  })

  it("переходит в режим редактирования и изменяет поля", () => {
    cy.contains("Редактировать").click()

    cy.get("input[name=phone]").clear().type("+7 999 111-22-33")
    cy.get("textarea[name=about]").clear().type("Новая информация о себе")

    cy.get("input[name=address]").clear().type("г. Москва, Новый адрес 42")

    cy.get("input[name=telegram]").clear().type("https://t.me/testuser123")
    cy.get("input[name=vk]").clear().type("https://vk.com/testuser456")

    cy.contains("Сохранить").click()

    cy.contains("+7 999 111-22-33")
    cy.contains("Новая информация о себе")
    cy.contains("testuser123")
    cy.contains("testuser456")
  })

  it("отменяет изменения при нажатии на 'Отмена'", () => {
    cy.contains("Редактировать").click()

    cy.get("input[name=phone]").clear().type("0000000000")
    cy.get("textarea[name=about]").clear().type("Удалить")

    cy.contains("Отмена").click()

    cy.contains("0000000000").should("not.exist")
    cy.contains("Удалить").should("not.exist")
  })

  it("меняет дату рождения", () => {
    cy.contains("Редактировать").click()

    cy.get("input[name=birthDate]").clear().type("2000-01-01")
    cy.contains("Сохранить").click()

    cy.contains("2000-01-01").should("exist")
  })

  it("меняет пол", () => {
    cy.contains("Редактировать").click()
    cy.get('[role="radio"][data-state="unchecked"]').click({ force: true })
    cy.contains("Сохранить").click()
    cy.contains("Женский")
  })

  it("переключает роль и делает редирект", () => {
    cy.contains("Преподаватель")
    cy.contains("Ученик").click()
    cy.url().should("include", "/student")
  })

  it("отображается корректно на мобильном экране", () => {
    cy.viewport(375, 667) // iPhone 6/7/8

    cy.visit("/profile")
    cy.contains("Профиль").should("be.visible")
    cy.get("img").should("be.visible")
    cy.contains("Контакты").should("be.visible")
  })

  it("загружает новый аватар", () => {
    cy.contains("Редактировать").click()

    cy.get('input[type="file"]').selectFile("cypress/fixtures/avatar.png", { force: true })

    cy.get("div").contains("О себе").parentsUntil("main").find("img")
      .should("have.attr", "src")
      .and("include", "blob:")
    cy.contains("Сохранить").click()
    cy.get("img").should("have.attr", "src").and("include", "blob:")
  })
})
