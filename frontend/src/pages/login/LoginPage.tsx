import {useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useLogin} from '@/features/auth/api/useAuth'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'

export default function LoginPage() {
  const navigate = useNavigate()
  const login = useLogin()
  const [form, setForm] = useState({username_or_email: '', password: ''})

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    login.mutate(form, {
      onSuccess: () => navigate('/catalog'),
    })
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Вход</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-4">
            <Input placeholder="Email или логин" value={form.username_or_email} onChange={e => setForm(s => ({...s, username_or_email: e.target.value}))} />
            <Input placeholder="Пароль" type="password" value={form.password} onChange={e => setForm(s => ({...s, password: e.target.value}))} />
            <Button type="submit" className="w-full" disabled={login.isPending}>{login.isPending ? 'Вход...' : 'Войти'}</Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Нет аккаунта? <Link to="/register" className="underline">Зарегистрироваться</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
