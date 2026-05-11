describe("Уведомления — страница", () => {
  beforeEach(() => {
    cy.visit("/login")

    cy.get('input[name="email"]').type("example@school.edu")
    cy.get('input[name="password"]').type("123456")
    cy.get("button[type=submit]").click()

    cy.url().should("include", "/teacher")
    cy.visit("/notifications")
  })

  it("отображает список уведомлений", () => {
    cy.get("h1").contains("Уведомления").should("be.visible")

    // Дождаться карточек
    cy.get("[data-testid=notification-card]").should("have.length.greaterThan", 0)
  })

  it("переходит по ссылке из уведомления", () => {
    cy.get("[data-testid=notification-card]")
      .contains("Перейти")
      .click()

    // Проверка — URL изменился
    cy.url().should("include", "/")
  })
})
