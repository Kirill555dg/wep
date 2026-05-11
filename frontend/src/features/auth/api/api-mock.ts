import { customAlphabet } from "nanoid"
import { mockUsers } from "@/entities/user/model/mock-users"
import { mockCredentials, addMockCredential } from "@/features/auth/lib/mock-auth"
import type { AuthApi } from "./api"
import type { User } from "@/entities/user/model/types"

export const authApiMock: AuthApi = {
  async login({ email, password }) {
    await new Promise((r) => setTimeout(r, 800))

    const expected = mockCredentials[email]
    if (!expected || expected !== password) {
      throw new Error("Неверный email или пароль")
    }

    const user = mockUsers.find((u) => u.email === email)
    if (!user) {
      throw new Error("Пользователь не найден")
    }

    return user
  },

  async register(data) {
    await new Promise((r) => setTimeout(r, 1000))

    const randomIndex = Math.floor(Math.random() * 5) + 1
    const avatar = `/avatar/${data.gender === "female" ? "female" : "male"}${randomIndex}.png`

    const nanoid = customAlphabet('0123456789', 5)

    const newUser: User = {
      id: Number(nanoid()),
      firstName: data.firstName,
      lastName: data.lastName,
      middleName: data.middleName,
      email: data.email,
      role: data.role,
      avatar: avatar
    }

    mockUsers.push(newUser)
    addMockCredential(data.email, data.password)

    return newUser
  },

  async resetPassword(email) {
    await new Promise((r) => setTimeout(r, 800))
    console.log(`🟡 Reset password email sent to: ${email}`)
  },

  async checkAuth() {
    await new Promise((r) => setTimeout(r, 300))
    const userJson = localStorage.getItem("auth-user") || sessionStorage.getItem("auth-user")
    if (!userJson) return null
    return JSON.parse(userJson) as User
  }
}
