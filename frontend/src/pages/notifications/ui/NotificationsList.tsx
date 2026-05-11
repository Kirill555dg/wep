import { Bell } from "lucide-react";
import { Notification } from "@/entities/notification/model/types";
import { NotificationCard } from "@/entities/notification/ui/NotificationCard";

interface Props {
  notifications: Notification[];
  onMarkRead: (id: number) => void;
  onNavigate: (link: string) => void;
}

export function NotificationsList({ notifications, onMarkRead, onNavigate }: Props) {
  if (notifications.length === 0) {
    return (
      <div className="text-center py-12">
        <Bell className="h-12 w-12 mx-auto text-gray-300 mb-4" />
        <h3 className="text-lg font-medium text-gray-500">Нет уведомлений</h3>
        <p className="text-gray-400 mt-1">У вас пока нет уведомлений в этой категории</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {notifications.map((notification) => (
        <NotificationCard
          key={notification.id}
          notification={notification}
          onMarkRead={onMarkRead}
          onNavigate={onNavigate}
        />
      ))}
    </div>
  );
}
