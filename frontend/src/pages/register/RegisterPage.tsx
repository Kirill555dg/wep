import {useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useRegister} from '@/features/auth/api/useAuth'
import {isValidEmail} from '@/shared/lib/utils'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/shared/ui/card'
import {Loader} from '@/shared/ui/loader'
import {BookOpen, Mail, Lock, User, Lock as LockIcon} from 'lucide-react'

export default function RegisterPage() {
  const navigate = useNavigate()
  const register = useRegister()
  const [form, setForm] = useState({
    email: '',
    password: '',
    confirm_password: '',
    first_name: '',
    last_name: '',
    username: '',
  })
  const [errors, setErrors] = useState<{[key: string]: string}>({})
  const [showPassword, setShowPassword] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: {[key: string]: string} = {}

    if (!form.email.trim()) {
      newErrors.email = 'Введите email'
    } else if (!isValidEmail(form.email)) {
      newErrors.email = 'Введите корректный email'
    }

    if (!form.password) {
      newErrors.password = 'Введите пароль'
    } else if (form.password.length < 8) {
      newErrors.password = 'Пароль должен содержать минимум 8 символов'
    }

    if (form.password !== form.confirm_password) {
      newErrors.confirm_password = 'Пароли не совпадают'
    }

    if (!form.first_name.trim()) {
      newErrors.first_name = 'Введите имя'
    }

    if (!form.last_name.trim()) {
      newErrors.last_name = 'Введите фамилию'
    }

    if (form.username && form.username.length < 3) {
      newErrors.username = 'Логин должен содержать минимум 3 символа'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    register.mutate({
      email: form.email,
      password: form.password,
      first_name: form.first_name,
      last_name: form.last_name,
      username: form.username || undefined,
    }, {
      onSuccess: () => navigate('/login'),
    })
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="space-y-3 text-center pb-6">
          <div className="flex justify-center mb-4">
            <div className="bg-blue-600 rounded-full p-4">
              <BookOpen className="h-8 w-8 text-white" />
            </div>
          </div>
          <CardTitle className="text-2xl">Создание аккаунта</CardTitle>
          <CardDescription>
            Зарегистрируйтесь для доступа к конструктору тестов
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={submit} className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Имя
                </label>
                <Input
                  placeholder="Иван"
                  value={form.first_name}
                  onChange={e => setForm(s => ({...s, first_name: e.target.value}))}
                  className={errors.first_name ? 'border-red-500' : ''}
                />
                {errors.first_name && (
                  <p className="text-sm text-red-600">{errors.first_name}</p>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Фамилия
                </label>
                <Input
                  placeholder="Иванов"
                  value={form.last_name}
                  onChange={e => setForm(s => ({...s, last_name: e.target.value}))}
                  className={errors.last_name ? 'border-red-500' : ''}
                />
                {errors.last_name && (
                  <p className="text-sm text-red-600">{errors.last_name}</p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Логин (опционально)
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <Input
                  placeholder="username"
                  value={form.username}
                  onChange={e => setForm(s => ({...s, username: e.target.value}))}
                  className={errors.username ? 'border-red-500 pl-10' : 'pl-10'}
                />
              </div>
              {errors.username && (
                <p className="text-sm text-red-600">{errors.username}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <Input
                  type="email"
                  placeholder="example@email.com"
                  value={form.email}
                  onChange={e => setForm(s => ({...s, email: e.target.value}))}
                  className={errors.email ? 'border-red-500 pl-10' : 'pl-10'}
                />
              </div>
              {errors.email && (
                <p className="text-sm text-red-600">{errors.email}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Пароль
              </label>
              <div className="relative">
                <LockIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <Input
                  type={showPassword ? 'text' : 'password'}
                  placeholder="••••••••"
                  value={form.password}
                  onChange={e => setForm(s => ({...s, password: e.target.value}))}
                  className={errors.password ? 'border-red-500 pl-10' : 'pl-10'}
                />
              </div>
              {errors.password && (
                <p className="text-sm text-red-600">{errors.password}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Подтверждение пароля
              </label>
              <Input
                type="password"
                placeholder="••••••••"
                value={form.confirm_password}
                onChange={e => setForm(s => ({...s, confirm_password: e.target.value}))}
                className={errors.confirm_password ? 'border-red-500' : ''}
              />
              {errors.confirm_password && (
                <p className="text-sm text-red-600">{errors.confirm_password}</p>
              )}
            </div>

            <Button
              type="submit"
              className="w-full"
              disabled={register.isPending}
            >
              {register.isPending ? (
                <>
                  <Loader className="mr-2 h-4 w-4" />
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
              <Link
                to="/login"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Войти
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
