import {useState} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useRegister} from '@/features/auth/api/useAuth'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'

export default function RegisterPage() {
  const navigate = useNavigate()
  const register = useRegister()
  const [form, setForm] = useState({email: '', password: '', first_name: '', last_name: '', username: '', full_name: ''})
  const [error, setError] = useState('')

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    register.mutate(form, {
      onSuccess: () => navigate('/login'),
      onError: (err: any) => setError(err.response?.data?.message || err.message),
    })
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <Card className="w-full max-w-md">
        <CardHeader><CardTitle>Регистрация</CardTitle></CardHeader>
        <CardContent>
          {error && <p className="mb-4 text-sm text-red-600">{error}</p>}
          <form onSubmit={submit} className="space-y-3">
            <Input placeholder="Email" type="email" value={form.email} onChange={e=>setForm(s=>({...s,email:e.target.value}))} />
            <Input placeholder="Пароль" type="password" value={form.password} onChange={e=>setForm(s=>({...s,password:e.target.value}))} />
            <Input placeholder="Имя" value={form.first_name} onChange={e=>setForm(s=>({...s,first_name:e.target.value}))} />
            <Input placeholder="Фамилия" value={form.last_name} onChange={e=>setForm(s=>({...s,last_name:e.target.value}))} />
            <Input placeholder="Логин" value={form.username} onChange={e=>setForm(s=>({...s,username:e.target.value}))} />
            <Input placeholder="Полное имя (опционально)" value={form.full_name} onChange={e=>setForm(s=>({...s,full_name:e.target.value}))} />
            <Button type="submit" className="w-full" disabled={register.isPending}>{register.isPending?'Регистрация...':'Зарегистрироваться'}</Button>
          </form>
          <p className="mt-4 text-center text-sm text-muted-foreground">
            Уже есть аккаунт? <Link to="/login" className="underline">Войти</Link>
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
