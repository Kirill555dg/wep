import { Navigate } from "react-router-dom";
import { useUserStore } from "@/entities/user/model/store";

export function MainRedirect() {
  const user = useUserStore((s) => s.user);

  if (user?.role === "teacher") return <Navigate to="/teacher" replace />;
  if (user?.role === "student") return <Navigate to="/student" replace />;
  return <Navigate to="/profile" replace />;
}
