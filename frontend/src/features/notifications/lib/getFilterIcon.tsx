import { getNotificationIcon } from "@/entities/notification/lib";
import { TabType } from "../model/types";
import { Filter, EyeOff } from "lucide-react";

export function getFilterIcon(type: TabType) {
  if (type === "all") return <Filter className="h-4 w-4 mr-2" />;
  if (type === "unread") return <EyeOff className="h-4 w-4 mr-2 text-gray-500" />;
  return getNotificationIcon(type);
}
