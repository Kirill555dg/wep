export {}
declare global {
  namespace Cypress {
    interface Chainable {
      loginAs(role: "teacher" | "student"): Chainable<void>
      logout(): Chainable<void>
      step(name: string): Chainable<void>
      api(method: "POST" | "GET" | "PATCH" | "DELETE", path: string, body?: object): Chainable<Response>
    }
  }
}

const USERS: Record<string, { email: string; password: string; name: string }> = {
  teacher: {
    email: "teacher@wep.dev",
    password: "TeacherPass123!",
    name: "Иван",
  },
  student: {
    email: "student@wep.dev",
    password: "StudentPass123!",
    name: "Петр",
  },
}

// Log in via API call, then inject token + user into AUT Zustand store
Cypress.Commands.add('loginAs', (role: 'teacher' | 'student') => {
  cy.step(`Login as ${role}`)
  const { email, password } = USERS[role]

  cy.request('POST', `${Cypress.env('API_URL')}/auth/login`, {
    username_or_email: email,
    password,
  }).then((res) => {
    expect(res.status).to.eq(200)
    const token = res.body.access_token
    const user = res.body.user
    Cypress.env('TOKEN', token)
    // Ensure AUT window exists, then write both token and user into Zustand
    cy.visit('/', { log: false })
    cy.window({ log: false }).then((win) => {
      // @ts-expect-error - global helper injected in main.tsx
      if (win.__setAuth) {
        // @ts-expect-error
        win.__setAuth(token, user)
      }
      cy.log(`Auth injected for ${user?.first_name ?? role} (${token.slice(0, 20)}...)`)
    })
  })
})

Cypress.Commands.add("logout", () => {
  cy.step("Logout")
  Cypress.env('TOKEN', null)
  cy.window({ log: false }).then((win) => {
    win.localStorage.removeItem('access_token')
  })
  cy.reload()
})

Cypress.Commands.add("step", (name: string) => {
  cy.log(`STEP: ${name}`)
})

Cypress.Commands.add("api", (method, path, body?) => {
  const token = Cypress.env('TOKEN')
  const headers: Record<string, string> = token ? { Authorization: `Bearer ${token}` } : {}
  return cy.request({
    method,
    url: `${Cypress.env('API_URL')}${path}`,
    headers,
    body,
    failOnStatusCode: false,
  })
})

beforeEach(() => {
  cy.clearLocalStorage()
  cy.clearCookies()
})
