import { Navigate, Outlet } from "react-router-dom";
import { useAuthStore } from "@/features/auth/model/store";
import { Loader } from "@/shared/ui/loader";
import { useUserStore } from "@/entities/user/model/store";

export default function RoleProtectedRoute({ requiredRole }: { requiredRole: "student" | "teacher" }) {
  const user = useUserStore((s) => s.user);
  const bootstrapped = useAuthStore((s) => s.bootstrapped);

  if (!bootstrapped) return <Loader />;

  if (!user || user.role !== requiredRole) {
    return <Navigate to="/profile" replace />;
  }

  return <Outlet />;
}
