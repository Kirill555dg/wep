import { useNavigate } from "react-router-dom";
import { useNotifications } from "@/features/notifications/model/useNotifications";
import { NotificationsHeader } from "@/pages/notifications/ui/NotificationsHeader";
import { NotificationsList } from "@/pages/notifications/ui/NotificationsList";
import { MainLayout } from "@/widgets/layout/MainLayout";

export default function NotificationsPage() {
  const { filteredNotifications, unreadCount, activeTab, setActiveTab, markAsRead, markAllAsRead } = useNotifications();

  const navigate = useNavigate();

  return (
    <MainLayout title="Уведомления" back={{ label: "На главную", to: "/" }}>
      <div className="w-full sm:max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        {/* Заголовок и кнопка "Прочитать всё" */}
        <NotificationsHeader
          unreadCount={unreadCount}
          activeTab={activeTab}
          onTabChange={setActiveTab}
          onMarkAllRead={markAllAsRead}
        />

        {/* Список уведомлений */}
        <NotificationsList notifications={filteredNotifications} onMarkRead={markAsRead} onNavigate={navigate} />
      </div>
    </MainLayout>
  );
}
