import { useEffect } from "react"
import { useNotificationStore } from "@/entities/notification/model/store"

export function useNotificationPreview() {
  const { notifications, fetch } = useNotificationStore()

  useEffect(() => {
    fetch()
  }, [fetch])

  const unread = notifications.filter((n) => !n.read)
  const unreadCount = unread.length
  const unreadPreview = unread.slice(0, 5)

  return { unreadCount, unreadPreview }
}
