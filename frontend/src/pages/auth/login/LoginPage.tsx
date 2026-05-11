import { AuthLayout } from "@/pages/auth/ui/AuthLayout";
import { LoginForm } from "@/pages/auth/login/ui/LoginForm";

export default function LoginPage() {
  return (
    <AuthLayout>
      <LoginForm />
    </AuthLayout>
  );
}
