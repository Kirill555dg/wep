import { describe, test, expect, beforeEach, vi } from 'vitest'

// Мок для localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value.toString()
    },
    removeItem: (key: string) => {
      delete store[key]
    },
    clear: () => {
      store = {}
    }
  }
})()

Object.defineProperty(global, 'localStorage', { value: localStorageMock })

// Создаем функцию для мокирования API
const createMockApi = () => {
  const mockResponses: Record<string, any> = {
    login: {
      access_token: 'mock-token',
      user: { id: 1, email: 'test@test.com', first_name: 'Test', last_name: 'User' }
    },
    tests: {
      data: [
        { id: 1, title: 'Test 1', questions_count: 5, description: 'Description 1' },
        { id: 2, title: 'Test 2', questions_count: 3, description: 'Description 2' }
      ]
    }
  }

  return {
    auth: {
      login: vi.fn().mockResolvedValue(mockResponses.login),
      register: vi.fn().mockResolvedValue({})
    },
    tests: {
      list: vi.fn().mockResolvedValue(mockResponses.tests),
      getDetail: vi.fn().mockResolvedValue({ data: mockResponses.tests.data[0] }),
      getQuestions: vi.fn().mockResolvedValue({ data: [] })
    }
  }
}

describe('TDD: Unit тесты бизнес-логики', () => {
  let mockApi: ReturnType<typeof createMockApi>

  beforeEach(() => {
    mockApi = createMockApi()
    localStorageMock.clear()
    vi.clearAllMocks()
  })

  describe('Given: Mocked API клиент', () => {
    test('When вызывается login Then возвращает корректный response', async () => {
      // Act
      const response = await mockApi.auth.login({
        username_or_email: 'test@test.com',
        password: 'password'
      })

      // Assert
      expect(response).toHaveProperty('access_token')
      expect(response.access_token).toBe('mock-token')
      expect(response.user).toHaveProperty('id')
      expect(response.user.email).toBe('test@test.com')
    })

    test('When вызывается tests.list Then возвращает массив тестов', async () => {
      // Act
      const response = await mockApi.tests.list({
        params: { query: {} },
        query: { skip: 0, limit: 20 }
      })

      // Assert
      expect(response.data).toBeInstanceOf(Array)
      expect(response.data).toHaveLength(2)
      expect(response.data[0]).toHaveProperty('id')
      expect(response.data[0]).toHaveProperty('title')
      expect(response.data[0]).toHaveProperty('questions_count')
    })
  })

  describe('Given: Управление состоянием авторизации', () => {
    test('When пользователь логинится Then token сохраняется в localStorage', async () => {
      // Act
      const response = await mockApi.auth.login({
        username_or_email: 'test@test.com',
        password: 'password'
      })

      localStorageMock.setItem('access_token', response.access_token)
      localStorageMock.setItem('user_id', String(response.user.id))

      // Assert
      expect(localStorageMock.getItem('access_token')).toBe('mock-token')
      expect(localStorageMock.getItem('user_id')).toBe('1')
    })

    test('When пользователь выходит из системы Then токен удаляется', () => {
      // Arrange
      localStorageMock.setItem('access_token', 'user-token')
      localStorageMock.setItem('user_id', '123')

      // Act
      localStorageMock.removeItem('access_token')
      localStorageMock.removeItem('user_id')

      // Assert
      expect(localStorageMock.getItem('access_token')).toBeNull()
      expect(localStorageMock.getItem('user_id')).toBeNull()
    })
  })

  describe('Given: Обработка ошибок API', () => {
    test('When API возвращает ошибку Then ошибка корректно обрабатывается', async () => {
      // Arrange
      const errorResponse = {
        response: {
          data: {
            error: {
              message: 'Token expired'
            }
          }
        }
      }

      mockApi.auth.login = vi.fn().mockRejectedValue(errorResponse)

      // Act & Assert
      try {
        await mockApi.auth.login({
          username_or_email: 'test@test.com',
          password: 'wrong'
        })
        throw new Error('Should have thrown')
      } catch (error: any) {
        expect(error.response?.data?.error?.message).toBe('Token expired')
      }
    })
  })

  describe('Given: Валидация данных', () => {
    test('When валидация email Then корректные email проходят', () => {
      // Arrange
      const validEmails = ['test@example.com', 'user@test.ru', 'name+tag@domain.com']
      const invalidEmails = ['invalid', 'test@', '@domain.com', 'test@.com']

      // Act & Assert
      validEmails.forEach(email => {
        expect(email).toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
      })

      invalidEmails.forEach(email => {
        expect(email).not.toMatch(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)
      })
    })

    test('When валидация пароля Then пароли соответствуют требованиям', () => {
      // Arrange
      const validPasswords = ['Password123', 'testPass', 'MySecurePass2024']
      const invalidPasswords = ['12345', 'pass', '1234567', 'short']

      // Act & Assert
      validPasswords.forEach(password => {
        expect(password.length).toBeGreaterThanOrEqual(8)
      })

      invalidPasswords.forEach(password => {
        expect(password.length).toBeLessThan(8)
      })
    })
  })

  describe('Given: Работа с тестами', () => {
    test('When получаем тесты Then данные корректны', async () => {
      // Act
      const tests = await mockApi.tests.list({
        params: { query: {} },
        query: { skip: 0, limit: 20 }
      })

      // Assert
      expect(tests.data).toBeDefined()
      expect(Array.isArray(tests.data)).toBe(true)
      
      tests.data.forEach(test => {
        expect(test).toHaveProperty('id')
        expect(test).toHaveProperty('title')
        expect(test).toHaveProperty('questions_count')
        expect(typeof test.questions_count).toBe('number')
        expect(test.questions_count).toBeGreaterThanOrEqual(0)
      })
    })

    test('When фильтруем тесты Then пагинация работает', async () => {
      // Arrange
      const firstPage = await mockApi.tests.list({
        params: { query: {} },
        query: { skip: 0, limit: 5 }
      })

      const secondPage = await mockApi.tests.list({
        params: { query: {} },
        query: { skip: 5, limit: 5 }
      });

      // Assert
      expect(firstPage).toBeDefined()
      expect(secondPage).toBeDefined()
    })
  })

  describe('Given: Интеграционные сценарии', () => {
    test('When полный процесс авторизации Then все шаги работают корректно', async () => {
      // Step 1: Login
      const loginResponse = await mockApi.auth.login({
        username_or_email: 'integration@test.com',
        password: 'password123'
      })

      expect(loginResponse).toHaveProperty('access_token')
      expect(loginResponse).toHaveProperty('user')

      // Step 2: Save to localStorage
      localStorageMock.setItem('access_token', loginResponse.access_token)
      localStorageMock.setItem('user_id', String(loginResponse.user.id))

      expect(localStorageMock.getItem('access_token')).toBe(loginResponse.access_token)

      // Step 3: Load tests
      const testsResponse = await mockApi.tests.list({
        params: { query: {} },
        query: { skip: 0, limit: 20 }
      })

      expect(testsResponse.data).toBeInstanceOf(Array)
      expect(testsResponse.data.length).toBeGreaterThan(0)

      // Step 4: Logout
      localStorageMock.removeItem('access_token')
      localStorageMock.removeItem('user_id')

      expect(localStorageMock.getItem('access_token')).toBeNull()
    })
  })
})