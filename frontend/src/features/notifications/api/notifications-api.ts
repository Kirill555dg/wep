import { Notification } from "@/entities/notification/model/types"
import { mockNotifications } from "@/entities/notification/model/mock-notifications"

export const notificationsApi = {
  async getAll(): Promise<Notification[]> {
    // моковый запрос
    return new Promise((resolve) => {
      setTimeout(() => resolve(mockNotifications), 300)
    })
  },

  async markAsRead(id: number): Promise<void> {
    // в реальности — PUT-запрос
    return new Promise((resolve) => setTimeout(resolve, 100))
  },

  async markAllAsRead(): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, 200))
  },
}
