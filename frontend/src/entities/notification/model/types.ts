export type NotificationType =
  | "homework_new"
  | "homework_graded"
  | "class_enrollment"
  | "class_expulsion"
  | "deadline"

export interface Notification {
  id: number
  type: NotificationType
  title: string
  description: string
  date: string
  read: boolean
  link: string
  linkText: string
  classTitle: string
}
