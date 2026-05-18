import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
    },
    baseUrl: 'http://localhost:5173',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 8000,
    pageLoadTimeout: 30000,
    requestTimeout: 8000,
    responseTimeout: 8000,
    chromeWebSecurity: false,
    experimentalStudio: true,
  },
  env: {
    API_URL: 'http://localhost:8023/api/v1',
    SLOW_MODE: false
  }
})
