import { Bell, Book, Calendar, CheckCircle, UserPlus, UserMinus } from "lucide-react";
import { NotificationType } from "../model/types";

export function getNotificationIcon(type: NotificationType) {
  switch (type) {
    case "homework_new":
      return <Book className="h-5 w-5 text-blue-500" />;
    case "homework_graded":
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case "class_enrollment":
      return <UserPlus className="h-5 w-5 text-purple-500" />;
    case "class_expulsion":
      return <UserMinus className="h-5 w-5 text-red-500" />;
    case "deadline":
      return <Calendar className="h-5 w-5 text-orange-500" />;
    default:
      return <Bell className="h-5 w-5 text-gray-500" />;
  }
}
