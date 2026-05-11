import { CardFooter } from "@/shared/ui/card";
import { Link } from "react-router-dom";
import { ReactNode } from "react";

type Props = {
  children?: ReactNode;
  linkText?: string;
  to?: string;
};

export function AuthCardFooter({ children, linkText, to }: Props) {
  return (
    <CardFooter className="flex flex-col space-y-4">
      {children}
      {linkText && to && (
        <div className="text-center text-sm">
          <Link to={to} className="text-blue-600 hover:underline font-medium flex items-center justify-center">
            {linkText}
          </Link>
        </div>
      )}
    </CardFooter>
  );
}
