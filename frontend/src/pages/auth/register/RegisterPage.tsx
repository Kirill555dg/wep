import { AuthLayout } from "@/pages/auth/ui/AuthLayout";
import { RegisterForm } from "@/pages/auth/register/ui/RegisterForm";

export default function RegisterPage() {
  return (
    <AuthLayout>
      <RegisterForm />
    </AuthLayout>
  );
}
