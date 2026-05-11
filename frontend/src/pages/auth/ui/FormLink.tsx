import { Link } from "react-router-dom";
import { type LucideIcon } from "lucide-react";
import { ReactNode } from "react";
import clsx from "clsx";

type Props = {
  to: string;
  children: ReactNode;
  icon?: LucideIcon;
  iconPosition?: "left" | "right";
  className?: string;
};

export function FormLink({ to, children, icon: Icon, iconPosition = "left", className }: Props) {
  return (
    <Link
      to={to}
      className={clsx(
        "text-blue-600 hover:underline font-medium",
        className,
        Icon && "flex items-center justify-center gap-1"
      )}
    >
      {Icon && iconPosition === "left" && <Icon className="h-4 w-4" />}
      {children}
      {Icon && iconPosition === "right" && <Icon className="h-4 w-4" />}
    </Link>
  );
}
