import { useEffect } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { toast } from 'react-hot-toast'

import { useAuth } from '@/shared/hooks/useAuth'
import { useRegister } from '@/features/auth/api/useAuth'
import { getApiError } from '@/shared/lib/api-error'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Label } from '@/shared/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'

const registerSchema = z.object({
  first_name: z.string().min(1, 'Обязательное поле'),
  last_name: z.string().min(1, 'Обязательное поле'),
  username: z.string().min(3, 'Минимум 3 символа'),
  email: z.string().email('Неверный email'),
  password: z.string().min(8, 'Минимум 8 символов'),
})

type RegisterForm = z.infer<typeof registerSchema>

export default function RegisterPage() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { isAuthed } = useAuth()
  const register = useRegister()

  useEffect(() => {
    if (isAuthed) {
      navigate('/catalog')
    }
  }, [isAuthed, navigate])

  const form = useForm<RegisterForm>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      first_name: '',
      last_name: '',
      username: '',
      email: '',
      password: '',
    },
  })

  const onSubmit = (values: RegisterForm) => {
    register.mutate(values, {
      onSuccess: () => {
        const redirect = searchParams.get('redirect')
        if (redirect) {
          navigate(`/login?redirect=${encodeURIComponent(redirect)}`)
        } else {
          navigate('/login')
        }
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
          <CardTitle className="text-lg font-medium">Создание аккаунта</CardTitle>
        </CardHeader>

        <CardContent className="space-y-4">
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="first_name">Имя</Label>
                <Input id="first_name" placeholder="Иван" {...form.register('first_name')} />
                {form.formState.errors.first_name && (
                  <p className="text-xs text-red-600">
                    {form.formState.errors.first_name.message}
                  </p>
                )}
              </div>

              <div className="space-y-1">
                <Label htmlFor="last_name">Фамилия</Label>
                <Input id="last_name" placeholder="Иванов" {...form.register('last_name')} />
                {form.formState.errors.last_name && (
                  <p className="text-xs text-red-600">
                    {form.formState.errors.last_name.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-1">
              <Label htmlFor="username">Логин</Label>
              <Input id="username" placeholder="username" {...form.register('username')} />
              {form.formState.errors.username && (
                <p className="text-xs text-red-600">
                  {form.formState.errors.username.message}
                </p>
              )}
            </div>

            <div className="space-y-1">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="example@email.com" {...form.register('email')} />
              {form.formState.errors.email && (
                <p className="text-xs text-red-600">
                  {form.formState.errors.email.message}
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

            <Button type="submit" className="w-full" disabled={register.isPending}>
              {register.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Регистрация...
                </>
              ) : (
                'Зарегистрироваться'
              )}
            </Button>
          </form>

          <div className="text-center text-sm">
            <p className="text-neutral-600">
              Уже есть аккаунт?{' '}
              <Link to="/login" className="text-blue-600 hover:text-blue-700 font-medium">
                Войти
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
