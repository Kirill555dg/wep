import { useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

import { useAuth } from '@/shared/hooks/useAuth'
import { useUserStore } from '@/entities/user/model/store'
import { useLogin } from '@/features/auth/api/useAuth'
import { getApiError } from '@/shared/lib/api-error'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'

const loginSchema = z.object({
  username_or_email: z.string().min(1, 'Введите email или логин'),
  password: z.string().min(8, 'Минимум 8 символов'),
})

type LoginForm = z.infer<typeof loginSchema>

export default function LoginPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthed } = useAuth()
  const login = useLogin()

  useEffect(() => {
    if (isAuthed) {
      navigate('/catalog')
    }
  }, [isAuthed, navigate])

  const form = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username_or_email: '',
      password: '',
    },
  })

  const onSubmit = (values: LoginForm) => {
    login.mutate(values, {
      onSuccess: (res) => {
        useUserStore.getState().setToken(res.data.access_token)
        useUserStore.getState().setUser(res.data.user)
        const redirect = searchParams.get('redirect') || '/catalog'
        navigate(redirect)
      },
      onError: (err) => {
        const { message } = getApiError(err)
        toast.error(message)
      },
    })
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <Card className="w-full max-w-sm">
        <CardHeader className="text-center pb-2">
          <h1 className="text-xl font-bold tracking-tight">WEP</h1>
          <CardTitle className="text-lg font-medium">Добро пожаловать</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="username_or_email">Email или логин</Label>
              <Input
                id="username_or_email"
                placeholder="example@email.com"
                {...form.register('username_or_email')}
              />
              {form.formState.errors.username_or_email && (
                <p className="text-xs text-red-600">
                  {form.formState.errors.username_or_email.message}
                </p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="password">Пароль</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                {...form.register('password')}
              />
              {form.formState.errors.password && (
                <p className="text-xs text-red-600">
                  {form.formState.errors.password.message}
                </p>
              )}
            </div>

            <Button type="submit" className="w-full" disabled={login.isPending}>
              {login.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Вход...
                </>
              ) : (
                'Войти'
              )}
            </Button>
          </form>

          <div className="text-center text-sm">
            <p className="text-neutral-600">
              Нет аккаунта?{' '}
              <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
