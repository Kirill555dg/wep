import { describe, it, expect, beforeEach } from "vitest"
import { useUserStore } from "@/entities/user/model/store"
import { mockUsers } from "@/entities/user/model/mock-users"

describe("userStore", () => {
  beforeEach(() => {
    useUserStore.setState({ user: null })
  })

  it("сохраняет пользователя", () => {
    const user = mockUsers[0]
    useUserStore.getState().setUser(user)
    expect(useUserStore.getState().user?.id).toBe(user.id)
  })

  it("очищает пользователя", () => {
    const user = mockUsers[0]
    useUserStore.getState().setUser(user)
    useUserStore.getState().setUser(null)
    expect(useUserStore.getState().user).toBeNull()
  })
})
