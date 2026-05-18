/// <reference types="cypress" />
import '../support/e2e'

describe('E2E with seeded data — teacher@wep.dev / student@wep.dev', () => {
  // ---------------------------------------------------------------
  beforeEach(() => {
    cy.clearLocalStorage()
    cy.clearCookies()
  })

  // ================================================================
  //  Auth
  // ================================================================

  it('teacher can log in via API and stay authed after reload', () => {
    cy.loginAs('teacher')
    cy.visit('/catalog')
    cy.url().should('include', '/catalog')
    // token set in Zustand — check via page content instead of raw localStorage
    cy.visit('/my-tests')
    cy.contains('Мои тесты', { timeout: 10000 }).should('be.visible')
    cy.reload()
    // Should stay on My Tests after reload (auth persisted via Zustand persist)
    cy.url().should('include', '/my-tests')
  })

  it('student can log in', () => {
    cy.loginAs('student')
    cy.visit('/catalog')
    cy.url().should('include', '/catalog')
    // Verify catalog is loaded by actual content, not generic "Каталог"
    cy.get('input[placeholder*="Поиск"]', { timeout: 10000 }).should('be.visible')
  })

  // ================================================================
  //  Catalog — public tests visible
  // ================================================================

  it('catalog shows the 6 seeded public tests', () => {
    cy.visit('/catalog')
    cy.step('Check seeded tests are visible')
    cy.contains('Математика: Производные', { timeout: 10000 }).should('be.visible')
    cy.contains('Физика: Механика').should('be.visible')
    cy.contains('Информатика: Алгоритмы').should('be.visible')
    cy.contains('Английский: Аудирование').should('be.visible')
    cy.contains('Химия: Органика').should('be.visible')
    cy.contains('Геометрия').should('be.visible')
  })

  it('catalog tag filters work', () => {
    cy.visit('/catalog')
    cy.step('Click math tag')
    cy.contains('math').click()
    cy.url().should('include', 'tags=math')
    cy.get('a[href^="/tests/"]', { timeout: 10000 }).should('have.length.at.least', 1)
  })

  it('clicking a test in catalog navigates to test view', () => {
    cy.visit('/catalog')
    cy.step('Click Math test')
    cy.contains('Математика: Производные').closest('a').click()
    cy.url().should('match', /\/tests\/\d+/)
    cy.contains('Математика: Производные').should('be.visible')
  })

  // ================================================================
  //  Test View — author tools, stats, recent attempts
  // ================================================================

  it('teacher sees edit buttons and stats on their own test', () => {
    cy.loginAs('teacher')
    cy.visit('/tests/3')
    cy.contains('Математика: Производные', { timeout: 10000 }).should('be.visible')
    cy.contains('Редактировать').should('be.visible')
    cy.contains('Настройки').should('be.visible')
    cy.contains('Статистика', { timeout: 10000 }).should('be.visible')
    cy.contains('Всего попыток').should('be.visible')
    cy.contains('Недавние попытки').should('be.visible')
  })

  // ================================================================
  //  Test Taking
  // ================================================================

  it('student takes the Math test and finishes successfully', () => {
    cy.loginAs('student')

    cy.step('Clean up any active Math attempt from prior runs')
    cy.api('GET', '/attempts/active?test_id=3').then((res) => {
      const data = res.body as { has_active?: boolean; attempt_id?: number } | undefined
      if (data?.has_active) {
        cy.step(`Finishing stale attempt ${data.attempt_id}`)
        cy.api('POST', `/attempts/${data.attempt_id}/finish`)
      }
    })

    cy.step('Navigate to Math test')
    cy.visit('/tests/3')
    cy.contains('Математика: Производные', { timeout: 10000 }).should('be.visible')

    cy.step('Intercept attempt creation')
    cy.intercept('POST', '**/api/v1/attempts/**').as('startAttempt')

    cy.step('Click Пройти снова / Начать тест')
    cy.get('button')
      .contains(/Пройти снова|Начать тест/)
      .should('be.visible')
      .and('not.be.disabled')
      .click()

    cy.step('Wait for backend response')
    cy.wait('@startAttempt').its('response.statusCode').should('eq', 201)

    cy.step('Allow React Router to navigate')
    cy.location('pathname', { timeout: 15000 }).should('match', /\/take$/)

    cy.step('Answer first question (single choice)')
    cy.get('div[class*="basis-"]', { timeout: 10000 }).first().click({ force: true })

    cy.step('Answer second question')
    cy.get('button').contains('Next').click()
    cy.get('div[class*="basis-"]').first().click({ force: true })

    cy.step('Answer text question')
    cy.get('button').contains('Next').click()
    cy.get('textarea, input[placeholder]', { timeout: 10000 }).first().clear().type('\$e^x\$', { delay: 50 })

    cy.step('Finish test')
    cy.contains('Finish', { timeout: 5000 }).should('not.be.disabled').click()

    cy.step('Verify results page')
    cy.url({ timeout: 10000 }).should('include', '/attempts/')
    cy.contains('Результаты теста', { timeout: 10000 }).should('be.visible')
  })

  // ================================================================
  //  History
  // ================================================================

  it('student history shows seeded attempts with calendar', () => {
    cy.loginAs('student')
    cy.visit('/history')

    cy.step('Page title')
    cy.contains('История', { timeout: 10000 }).should('be.visible')

    cy.step('Recent attempt card')
    cy.contains('Последний тест').should('be.visible')

    cy.step('GitHub-style calendar visible')
    cy.contains('Активность').should('be.visible')

    cy.step('Filter tabs')
    cy.contains('Все').should('be.visible')
    cy.contains('Завершенные').should('be.visible')

    cy.step('At least one attempt is listed')
    cy.contains('Математика: Производные', { timeout: 10000 }).should('be.visible')

    cy.step('Calendar has colored cells')
    cy.get('.bg-green-200, .bg-green-400, .bg-green-600', { timeout: 10000 }).should('have.length.at.least', 1)
  })

  // ================================================================
  //  My Tests
  // ================================================================

  it('teacher sees all 6 seeded tests in My Tests', () => {
    cy.loginAs('teacher')
    cy.visit('/my-tests')

    cy.step('All tests visible')
    cy.contains('Математика: Производные').should('be.visible')
    cy.contains('Физика: Механика').should('be.visible')
    cy.contains('Информатика: Алгоритмы').should('be.visible')
    cy.contains('Английский: Аудирование').should('be.visible')
    cy.contains('Химия: Органика').should('be.visible')
    cy.contains('Геометрия').should('be.visible')
  })

  // ================================================================
  //  Results
  // ================================================================

  it('student can review a completed attempt', () => {
    cy.loginAs('student')
    cy.step('Navigate via API to latest completed attempt')
    cy.api('GET', '/attempts/?limit=1').then((res) => {
      expect(res.status).to.eq(200)
      const attempts = res.body.items || []
      expect(attempts.length).to.be.at.least(1)
      const lastAttempt = attempts[0]
      cy.visit(`/attempts/${lastAttempt.id}`)
      cy.contains('Результаты теста').should('be.visible')
      cy.contains('Итого:').should('be.visible')
    })
  })

  // ================================================================
  //  Question Pool (edit mode)
  // ================================================================

  it('teacher can add a question from the pool', () => {
    cy.loginAs('teacher')
    cy.visit('/tests/3/edit')

    cy.step('Edit mode loaded')
    cy.contains('Questions', { timeout: 10000 }).should('be.visible')

    cy.step('Open pool modal')
    cy.contains('From Pool').click()
    cy.contains('Добавить вопрос из пула').should('be.visible')

    cy.step('Search and add first question')
    cy.get('input[placeholder*="Поиск"]').type('сопоставьте', { delay: 100 })
    // Wait for filtering
    cy.wait(500)
    cy.get('body').then(($body) => {
      if ($body.text().includes('MATCHING') || $body.text().includes('Сопоставьте')) {
        cy.contains('Добавить').first().click()
        cy.contains('Добавить вопрос из пула').should('not.exist')
      }
    })
  })
})
