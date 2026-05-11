describe("Блок авторизации", () => {
  const validEmail = "teacher@school.edu"
  const validPassword = "123456"

  it("Успешный вход", () => {
    cy.visit("/login")
    cy.get('input[name="email"]').type(validEmail)
    cy.get('input[name="password"]').type(validPassword)
    cy.get('button[type="submit"]').click()
    cy.url().should("eq", `${Cypress.config().baseUrl}/teacher`)
  })

  it("Ошибка при неверном пароле", () => {
    cy.visit("/login")
    cy.get('input[name="email"]').type(validEmail)
    cy.get('input[name="password"]').type("wrongpass")
    cy.get('button[type="submit"]').click()
    cy.contains("Неверная почта или пароль.").should("exist")
    cy.url().should("include", "/login")
  })

  it("Переход на страницу регистрации", () => {
    cy.visit("/login")
    cy.contains("Зарегистрироваться").click()
    cy.url().should("include", "/register")
  })

  it("Переход на восстановление пароля", () => {
    cy.visit("/login")
    cy.contains("Забыли пароль").click()
    cy.url().should("include", "/reset-password")
  })

  it("Восстановление пароля", () => {
    cy.visit("/reset-password")
    cy.get('input[name="email"]').type(validEmail)
    cy.get('button[type="submit"]').click()
    cy.contains("Мы отправили инструкции по восстановлению пароля").should("exist")
  })

  it("Успешная регистрация нового ученика", () => {
    const email = `student${Date.now()}@test.ru`
    cy.visit("/register")

    cy.get('input[name="lastName"]').type("Иванов")
    cy.get('input[name="firstName"]').type("Иван")
    cy.get('input[name="middleName"]').type("Петрович")
    cy.get('input[name="email"]').type(email)
    cy.get('input[name="password"]').type("123456")
    cy.get('input[name="confirmPassword"]').type("123456")
    cy.get('input[name="dateOfBirth"]').type("2000-01-01")
    cy.get('textarea[name="description"]').type("Я тестовый пользователь")
    cy.contains("Ученик").click()
    cy.contains("Я принимаю условия использования").click()
    cy.get('button[type="submit"]').click()

    cy.url().should("eq", `${Cypress.config().baseUrl}/student`)
  })

  it("Ошибка при незаполненных полях регистрации", () => {
    cy.visit("/register")
    cy.get('button[type="submit"]').click()
    cy.contains("Введите имя").should("exist")
    cy.contains("Введите фамилию").should("exist")
    cy.contains("Введите корректный email").should("exist")
    cy.contains("Подтвердите пароль").should("exist")
  })
})
