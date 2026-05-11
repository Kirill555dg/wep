import { useNotificationStore } from "../model/store"

export function refreshNotifications() {
  const store = useNotificationStore.getState()
  store.invalidate()
  store.fetch()
}
