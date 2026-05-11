import { create } from "zustand"
import { Notification } from "./types"
import { notificationsApi } from "@/features/notifications/api/notifications-api"

interface NotificationStore {
  notifications: Notification[]
  initialized: boolean
  fetch: () => Promise<void>
  markAsRead: (id: number) => Promise<void>
  markAllAsRead: () => Promise<void>
  invalidate: () => void
}

export const useNotificationStore = create<NotificationStore>((set, get) => ({
  notifications: [],
  initialized: false,

  async fetch() {
    if (get().initialized) return
    const data = await notificationsApi.getAll()
    set({ notifications: data, initialized: true })
  },

  async markAsRead(id) {
    await notificationsApi.markAsRead(id)
    set((state) => ({
      notifications: state.notifications.map((n) =>
        n.id === id ? { ...n, read: true } : n
      ),
    }))
  },

  async markAllAsRead() {
    await notificationsApi.markAllAsRead()
    set((state) => ({
      notifications: state.notifications.map((n) => ({
        ...n,
        read: true,
      })),
    }))
  },

  invalidate() {
    set({ initialized: false })
  },
}))
