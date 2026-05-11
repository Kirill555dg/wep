import { Book, Star, UserPlus, UserMinus, Calendar, Filter, EyeOff } from "lucide-react";
import { NotificationType } from "@/entities/notification/model/types";

export type TabType = "all" | "unread" | NotificationType;

export const filterOptions: {
  value: TabType;
  label: string;
}[] = [
  { value: "all", label: "Все" },
  { value: "unread", label: "Непрочитанные" },
  { value: "homework_new", label: "Новые задания" },
  { value: "homework_graded", label: "Оценённые" },
  { value: "class_enrollment", label: "Зачисления" },
  { value: "class_expulsion", label: "Отчисления" },
  { value: "deadline", label: "Дедлайны" },
];
