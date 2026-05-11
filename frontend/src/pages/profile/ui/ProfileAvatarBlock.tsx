import { useRef } from "react";
import { Button } from "@/shared/ui/button";
import { Camera } from "lucide-react";
import { UserAvatar } from "@/entities/user/ui/UserAvatar";

interface Props {
  fullName: string;
  avatarUrl?: string;
  isEditing: boolean;
  activeRole: "teacher" | "student";
  onSwitchRole: (role: "teacher" | "student") => void;
  roleSwitchVisible?: boolean;
  onAvatarChange?: (file: File | null) => void;
}

export function ProfileAvatarBlock({
  fullName,
  avatarUrl,
  isEditing,
  activeRole,
  onSwitchRole,
  onAvatarChange,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (onAvatarChange) onAvatarChange(file);
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        <UserAvatar avatar={avatarUrl} size="h-32 w-32 sm:h-48 sm:w-48" className="border-2" />

        {isEditing && (
          <>
            <Button
              size="icon"
              className="absolute bottom-0 right-0 rounded-full h-10 w-10 bg-blue-600 hover:bg-blue-700"
              onClick={handleAvatarClick}
              type="button"
            >
              <Camera className="h-5 w-5 text-white" />
            </Button>
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleFileChange} />
          </>
        )}
      </div>

      <h2 className="text-xl font-bold mt-4 text-center">{fullName}</h2>

      <div className="mt-6 flex gap-2 w-full">
        <Button
          variant={activeRole === "student" ? "default" : "outline"}
          className="flex-1"
          onClick={() => onSwitchRole("student")}
        >
          Ученик
        </Button>
        <Button
          variant={activeRole === "teacher" ? "default" : "outline"}
          className="flex-1"
          onClick={() => onSwitchRole("teacher")}
        >
          Преподаватель
        </Button>
      </div>
    </div>
  );
}
