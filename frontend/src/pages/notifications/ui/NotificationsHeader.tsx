import { Bell, CheckCheck } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { NotificationsFilterDropdown } from "@/features/notifications/ui/NotificationsFilterDropdown";
import { TabType } from "@/features/notifications/model/types";

interface Props {
  unreadCount: number;
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  onMarkAllRead: () => void;
}

export function NotificationsHeader({ unreadCount, activeTab, onTabChange, onMarkAllRead }: Props) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
      {/* Левая зона: Заголовок */}
      <div className="flex items-center text-2xl font-bold text-gray-900">
        <Bell className="h-6 w-6 mr-2" />
        Уведомления
        {unreadCount > 0 && (
          <Badge className="ml-2" variant="secondary">
            {unreadCount}
          </Badge>
        )}
      </div>

      {/* Кнопка "Прочитать все" */}
      <Button variant="outline" size="sm" onClick={onMarkAllRead} disabled={unreadCount === 0}>
        <CheckCheck className="h-4 w-4 mr-2" />
        <span className="hidden sm:inline">Прочитать все</span>
      </Button>

      {/* Фильтр — адаптивен */}
      <div className="order-last sm:order-none flex-1 w-min=[200px]">
        <NotificationsFilterDropdown value={activeTab} onChange={onTabChange} />
      </div>
    </div>
  );
}
