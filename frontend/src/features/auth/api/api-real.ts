import type { AuthApi } from "./api"
import type { User } from "@/entities/user/model/types"
import type { LoginData, RegisterData } from "@/features/auth/model/schema"
import { axiosInstance } from "@/shared/api/axios"

export const authApiReal: AuthApi = {
  async login(data: LoginData): Promise<User> {
    const res = await axiosInstance.post("/auth/login", data)
    return res.data
  },

  async register(data: RegisterData): Promise<User> {
    const res = await axiosInstance.post("/auth/register", data)
    return res.data
  },

  async resetPassword(email: string): Promise<void> {
    await axiosInstance.post("/auth/reset-password", { email })
  },

  async checkAuth(): Promise<User | null> {
    try {
      const res = await axiosInstance.get("/auth/check")
      return res.data
    } catch {
      return null
    }
  }
}