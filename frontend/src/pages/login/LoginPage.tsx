import {useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useLogin} from '@/features/auth/api/useAuth'
import {isValidEmail} from '@/shared/lib/utils'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from '@/shared/ui/card'
import {Loader} from '@/shared/ui/loader'
import {BookOpen, Lock, User} from 'lucide-react'

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useLogin()
  const [form, setForm] = useState({username_or_email: '', password: ''})
  const [errors, setErrors] = useState<{[key: string]: string}>({})
  const [showPassword, setShowPassword] = useState(false)

  const validateForm = (): boolean => {
    const newErrors: {[key: string]: string} = {}

    if (!form.username_or_email.trim()) {
      newErrors.username_or_email = 'Введите email или пароль'
    } else if (!isValidEmail(form.username_or_email) && form.username_or_email.length < 3) {
      newErrors.username_or_email = 'Введите корректный email или логин (минимум 3 символа)'
    }

    if (!form.password) {
      newErrors.password = 'Введите пароль'
    } else if (form.password.length < 8) {
      newErrors.password = 'Пароль должен содержать минимум 8 символов'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return

    login.mutate(form, {
      onSuccess: () => navigate('/catalog'),
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
          <CardTitle className="text-2xl">Добро пожаловать</CardTitle>
          <CardDescription>
            Войдите в свою учетную запись для доступа к тестам
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          <form onSubmit={submit} className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">
                Email или логин
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
                <Input
                  placeholder="example@email.com"
                  value={form.username_or_email}
                  onChange={e => setForm(s => ({...s, username_or_email: e.target.value}))}
                  className={errors.username_or_email ? 'border-red-500 pl-10' : 'pl-10'}
                />
              </div>
              {errors.username_or_email && (
                <p className="text-sm text-red-600">{errors.username_or_email}</p>
              )}
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">
                Пароль
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-neutral-400" />
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

            <Button
              type="submit"
              className="w-full"
              disabled={login.isPending}
            >
              {login.isPending ? (
                <>
                  <Loader className="mr-2 h-4 w-4" />
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
              <Link
                to="/register"
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Зарегистрироваться
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
