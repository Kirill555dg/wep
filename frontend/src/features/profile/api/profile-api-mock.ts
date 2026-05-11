import type { ProfileApi } from "./profile-api"
import type { User } from "@/entities/user/model/types"

export const profileApiMock: ProfileApi = {
  async updateProfile(data) {
    await new Promise((r) => setTimeout(r, 300))
    const storage = localStorage.getItem("auth-user") ? localStorage : sessionStorage
    const user = JSON.parse(storage.getItem("auth-user") || "{}")
    const updated: User = { ...user, ...data }
    storage.setItem("auth-user", JSON.stringify(updated))
    return updated
  },
}
