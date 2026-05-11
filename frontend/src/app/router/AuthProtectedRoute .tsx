import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/features/auth/model/store";
import { Loader } from "@/shared/ui/loader";
import { useUserStore } from "@/entities/user/model/store";

export default function AuthProtectedRoute() {
  const user = useUserStore((s) => s.user);
  const bootstrapped = useAuthStore((s) => s.bootstrapped);

  if (!bootstrapped) return <Loader />;

  if (!user) return <Navigate to="/login" replace />;

  return <Outlet />;
}
