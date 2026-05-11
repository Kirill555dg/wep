import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, LoginData } from "@/features/auth/model/schema";
import { useAuthStore } from "@/features/auth/model/store";
import { useNavigate } from "react-router-dom";

import { Button } from "@/shared/ui/button";
import { Card, CardContent } from "@/shared/ui/card";
import { Mail, Lock } from "lucide-react";
import { toast } from "@/shared/lib/toast";
import {
  AuthCardFooter,
  AuthCardHeader,
  FormCheckbox,
  FormErrorAlert,
  FormFieldWithIcon,
  FormLink,
} from "@/pages/auth/ui";
import { useUserStore } from "@/entities/user/model/store";

export function LoginForm() {
  const navigate = useNavigate();

  const login = useAuthStore((s) => s.login);
  const error = useAuthStore((s) => s.error);
  const setError = useAuthStore((s) => s.setError);
  const isLoading = useAuthStore((s) => s.loading);

  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
  });

  const onSubmit = async (data: LoginData) => {
    setError(null);
    try {
      await login(data);
      const role = useUserStore.getState().user?.role;
      toast.info("Успешный вход", `Вы вошли как ${role === "teacher" ? "преподаватель" : "ученик"}`);
      navigate(`/${role}`);
    } catch (_) {
      setError("Неверная почта или пароль.");
    }
  };

  return (
    <Card>
      <AuthCardHeader
        title="Вход в систему"
        description="Войдите в свою учетную запись для доступа к образовательной платформе"
      />
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <FormErrorAlert message={error} />

          <FormFieldWithIcon
            id="email"
            label="Email"
            placeholder="example@edu.ru"
            type="email"
            icon={Mail}
            error={errors.email}
            registerProps={register("email")}
          />

          <FormFieldWithIcon
            id="password"
            label="Пароль"
            type="password"
            placeholder="••••••••"
            icon={Lock}
            error={errors.password}
            registerProps={register("password")}
          />
          <div className="flex items-center justify-between">
            <FormCheckbox name="rememberMe" control={control} label="Запомнить меня" />

            <div className="text-right text-sm">
              <FormLink to="/reset-password">Забыли пароль?</FormLink>
            </div>
          </div>
          <Button type="submit" className="w-full" disabled={isLoading}>
            Войти
          </Button>
        </form>
      </CardContent>
      <AuthCardFooter>
        <p className="text-sm text-gray-600 text-center">
          Нет учетной записи? <FormLink to="/register">Зарегистрироваться</FormLink>
        </p>
      </AuthCardFooter>
    </Card>
  );
}
