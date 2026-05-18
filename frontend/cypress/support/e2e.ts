export {}
declare global {
  namespace Cypress {
    interface Chainable {
      loginAs(role: string): Chainable<void>
      logout(): Chainable<void>
      step(name: string): Chainable<void>
    }
  }
}

// Команда авторизации с существующим пользователем
Cypress.Commands.add('loginAs', (role: string) => {
  cy.clearLocalStorage()
  cy.clearCookies()
  cy.visit('/login')

  const username = role === 'teacher' ? 'teacher' : 'student'

  cy.get('[placeholder*="Email"]').type(`${username}@example.edu`)
  cy.get('[placeholder*="Пароль"]').type('password123')
  cy.contains('Войти').click()

  cy.url().should('not.include', '/login')
})

// Команда выхода из системы
Cypress.Commands.add('logout', () => {
  cy.visit('/')
  cy.get('[role="button"]').filter(':contains("Выйти")').click()
  cy.url().should('include', '/login')
})

// Команда для логирования шагов
Cypress.Commands.add('step', (name: string) => {
  cy.log(`📋 ${name}`)
})

// Настройка куки для тестового режима
beforeEach(() => {
  // Сброс состояния перед каждым тестом
  cy.clearLocalStorage()
  cy.clearCookies()
  
  // Установить тестовый режим
  cy.window().then((win) => {
    win.localStorage.setItem('__TEST_MODE__', 'true')
  })
})

// Глобальная конфигурация для медленного режима (при отладке)
if (Cypress.env('SLOW_MODE')) {
  const originalCommand = Cypress.log
  Cypress.log = function (options) {
    options.consoleProps = () => {
      return {
        'Test Duration (ms)': Date.now() - Cypress.config('defaultCommandTimeout')
      }
    }
    return originalCommand(options)
  }
  
  Cypress.config('defaultCommandTimeout', 10000)
  Cypress.config('pageLoadTimeout', 20000)
}
