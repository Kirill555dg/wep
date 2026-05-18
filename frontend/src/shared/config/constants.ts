export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:8023',
} as const

export const APP_CONFIG = {
  APP_NAME: 'Test Constructor',
  VERSION: '1.0.0',
} as const

export const ROUTES = {
  LOGIN: '/login',
  REGISTER: '/register',
  CATALOG: '/catalog',
  EDITOR: '/editor',
  TEST_TAKING: '/test-taking/:id',
  RESULTS: '/results/:id',
  PROFILE: '/profile',
  STATS: '/stats',
} as const

export const QUESTION_TYPES = {
  SINGLE_CHOICE: 'single_choice',
  MULTIPLE_CHOICE: 'multiple_choice',
  TEXT: 'text',
  ESSAY: 'essay',
} as const

export const ATTEMPT_STATUS = {
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  EXPIRED: 'expired',
  ABANDONED: 'abandoned',
} as const

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
} as const
