import { Avatar, AvatarFallback, AvatarImage } from "@/shared/ui/avatar";
import { useUserStore } from "../model/store";

interface UserAvatarProps {
  avatar?: string;
  className?: string;
  size?: string; // e.g. "h-10 w-10"
}

export function UserAvatar({ avatar, className = "", size = "h-10 w-10" }: UserAvatarProps) {
  const user = useUserStore((s) => s.user);

  const initials = [user!.firstName, user!.lastName]
    .map((n) => n?.[0])
    .join("")
    .toUpperCase();

  return (
    <Avatar className={`${size} ${className}`}>
      <AvatarImage
        src={avatar ? avatar : user!.avatar}
        alt={user!.firstName}
        className="object-cover h-full w-full rounded-full"
      />
      <AvatarFallback>{initials}</AvatarFallback>
    </Avatar>
  );
}
