export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  const time = date.toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" })

  if (diffDays === 0) return `Сегодня, ${time}`
  if (diffDays === 1) return `Вчера, ${time}`
  return `${date.toLocaleDateString("ru-RU", { day: "numeric", month: "long" })}, ${time}`
}
