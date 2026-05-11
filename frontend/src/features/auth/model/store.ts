import { create } from "zustand"
import { authApi } from "@/features/auth/api/api"
import type { LoginData, RegisterData } from "./schema"
import { useUserStore } from "@/entities/user/model/store"

interface AuthState {
  loading: boolean
  error: string | null
  bootstrapped: boolean

  login: (data: LoginData) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
  setError: (message: string | null) => void
  setBootstrapped: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  loading: false,
  error: null,
  bootstrapped: false,

  async login(data) {
    set({ loading: true, error: null })
    try {
      const user = await authApi.login(data)
      const storage = data.rememberMe ? localStorage : sessionStorage
      storage.setItem("auth-user", JSON.stringify(user))
      useUserStore.getState().setUser(user)
    } catch (e: any) {
      set({ error: e.message || "Ошибка авторизации" })
      throw e
    } finally {
      set({ loading: false })
    }
  },

  async register(data) {
    set({ loading: true, error: null })
    try {
      const user = await authApi.register(data)
      useUserStore.getState().setUser(user)
    } catch (e: any) {
      set({ error: e.message || "Ошибка регистрации" })
      throw e
    } finally {
      set({ loading: false })
    }
  },

  async checkAuth() {
    set({ loading: true })
    try {
      const user = await authApi.checkAuth()
      if (user) {
        useUserStore.getState().setUser(user)
      }
    } finally {
      set({ loading: false })
    }
  },

  logout() {
    localStorage.removeItem("auth-user")
    sessionStorage.removeItem("auth-user")
    useUserStore.getState().setUser(null)
  },

  setError(message) {
    set({ error: message })
  },

  setBootstrapped() {
    set({ bootstrapped: true })
  },
}))
