import { cn } from "@/shared/lib/utils";
import Telegram from "@/shared/assets/icons/Telegram";
import Github from "@/shared/assets/icons/Github";
import Vk from "@/shared/assets/icons/Vk";

const icons = {
  telegram: Telegram,
  github: Github,
  vk: Vk,
} as const;

type SocialType = keyof typeof icons;

interface Props {
  type: SocialType;
  className?: string;
}

export function SocialIcon({ type, className }: Props) {
  const Icon = icons[type];
  return <Icon className={cn("w-5 h-5", className)} />;
}
