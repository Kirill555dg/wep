import { Check } from "lucide-react";
import { Card, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Notification } from "../model/types";
import { getNotificationIcon, getNotificationBadge } from "../lib";
import { formatDate } from "../lib/formatDate";

interface NotificationCardProps {
  notification: Notification;
  onMarkRead?: (id: number) => void;
  onNavigate?: (link: string) => void;
}

export function NotificationCard({ notification, onMarkRead, onNavigate }: NotificationCardProps) {
  return (
    <Card
      data-testid="notification-card"
      className={`overflow-hidden transition-colors ${notification.read ? "bg-white" : "bg-blue-50 border-blue-100"}`}
    >
      <CardContent className="p-0">
        <div className="p-4">
          <div className="flex items-start">
            <div className="mr-3 mt-1 flex-shrink-0">{getNotificationIcon(notification.type)}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1 flex-wrap gap-2">
                <div className="flex items-center">
                  <h3 className="font-medium text-gray-900">{notification.title}</h3>
                  {!notification.read && <span className="ml-2 h-2 w-2 rounded-full bg-blue-500" aria-hidden="true" />}
                </div>
                <span className="text-xs text-gray-500">{formatDate(notification.date)}</span>
              </div>

              <div className="mb-2 text-sm text-gray-600">{notification.description}</div>

              <div className="flex items-center justify-between flex-wrap gap-y-2">
                <div className="flex items-center space-x-2">
                  {getNotificationBadge(notification.type)}
                  <span className="text-xs text-gray-500">{notification.classTitle}</span>
                </div>

                <div className="flex flex-wrap space-x-2">
                  {!notification.read && onMarkRead && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 px-2 text-gray-500"
                      onClick={(e) => {
                        e.stopPropagation();
                        onMarkRead(notification.id);
                      }}
                    >
                      <Check className="h-4 w-4 mr-1" />
                      <span className="text-xs">Прочитано</span>
                    </Button>
                  )}

                  {onNavigate && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8"
                      onClick={() => {
                        if (!notification.read && onMarkRead) {
                          onMarkRead(notification.id);
                        }
                        onNavigate(notification.link);
                      }}
                    >
                      {notification.linkText}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
