import { useEffect, useMemo, useState } from "react"
import { TabType } from "./types"
import { useNotificationStore } from "@/entities/notification/model/store"

export function useNotifications() {
  const {
    notifications,
    markAsRead,
    markAllAsRead,
    fetch,
  } = useNotificationStore()

  const [activeTab, setActiveTab] = useState<TabType>("all")

  useEffect(() => {
    fetch()
  }, [fetch])

  const filteredNotifications = useMemo(() => {
    return notifications.filter((n) => {
      if (activeTab === "all") return true
      if (activeTab === "unread") return !n.read
      return n.type === activeTab
    })
  }, [notifications, activeTab])

  const unreadCount = useMemo(() => {
    return notifications.filter((n) => !n.read).length
  }, [notifications])

  return {
    activeTab,
    setActiveTab,
    filteredNotifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
  }
}
