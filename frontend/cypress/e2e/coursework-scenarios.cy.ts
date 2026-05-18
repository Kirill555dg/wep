import { default as user } from '../fixtures/user.json'
declare global {
  namespace Cypress {
    interface Chainable {
      loginAs(role: string): Chainable<void>
      logout(): Chainable<void>
      step(name: string): Chainable<void>
    }
  }
}

describe('Coursework User Scenarios - E2E', () => {
  it('Teacher creates public test', () => {
    cy.step('1. Teacher login')
    cy.loginAs('teacher')
    cy.url().should('include', '/catalog')

    cy.step('2. Create test')
    cy.visit('/editor')
    cy.get('[placeholder*="Название"]').type('Тест по математике')
    cy.get('[placeholder*="Описание"]').type('Пример теста для курсовой')

    cy.step('3. Add question with formulas')
    cy.contains('Добавить вопрос').click()
    cy.get('[placeholder*="Текст вопроса"]').type('Чему равна производная f(x) = x³?')

    cy.step('4. Set public access')
    cy.contains('Публичный').click()
    cy.contains('Опубликовать').click()

    cy.step('5. Verify in catalog')
    cy.visit('/catalog')
    cy.contains('Тест по математике').should('be.visible')
  })

  it('Student takes test', () => {
    cy.loginAs('student')
    cy.visit('/catalog')
    cy.contains('Тест по математике').click()
    cy.contains('Начать тест').click()
    cy.get('.question-option').first().click()
    cy.contains('Следующий').click()
    cy.contains('Завершить').click()
    cy.contains('Результаты').should('be.visible')
  })
})

beforeEach(() => {
  cy.clearLocalStorage()
  cy.clearCookies()
})
