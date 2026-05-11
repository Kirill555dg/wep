import { describe, beforeEach, it, expect } from "vitest"
import { useAuthStore } from "@/features/auth/model/store"
import { setAuthApi } from "@/features/auth/api/api"
import { authApiMock } from "@/features/auth/api/api-mock"
import { useUserStore } from "@/entities/user/model/store"
import { mockUsers } from "@/entities/user/model/mock-users"
import type { LoginData, RegisterData } from "@/features/auth/model/schema"

beforeEach(() => {
  useAuthStore.setState({
    loading: false,
    error: null,
    bootstrapped: false,
  })
  useUserStore.setState({ user: null })
  localStorage.clear()
  sessionStorage.clear()

  setAuthApi(authApiMock)
})

describe("authStore", () => {
  it("входит с валидными данными", async () => {
    const user = mockUsers[0]
    const credentials: LoginData = {
      email: user.email,
      password: "123456",
      rememberMe: true,
    }

    await useAuthStore.getState().login(credentials)
    expect(useUserStore.getState().user?.email).toBe(user.email)
  })

  it("регистрирует нового пользователя", async () => {
    const newUser: RegisterData = {
      firstName: "Алексей",
      lastName: "Сидоров",
      middleName: "",
      email: "new@edu.ru",
      password: "abcdef",
      confirmPassword: "abcdef",
      role: "student",
      gender: "male",
      agreeTerms: true,
    }

    await useAuthStore.getState().register(newUser)
    expect(useUserStore.getState().user?.email).toBe(newUser.email)
    expect(useUserStore.getState().user?.role).toBe("student")
  })

  it("сбрасывает пользователя при logout", async () => {
    const user = mockUsers[0]
    useUserStore.getState().setUser(user)

    useAuthStore.getState().logout()
    expect(useUserStore.getState().user).toBeNull()
  })

  it("подтверждает авторизацию через checkAuth", async () => {
    const user = mockUsers[0]
    localStorage.setItem("auth-user", JSON.stringify(user))

    await useAuthStore.getState().checkAuth()
    expect(useUserStore.getState().user?.email).toBe(user.email)
  })
})
