import {useNavigate} from 'react-router-dom'
import {useUserStore} from '@/entities/user/model/store'
import {useAuthorStats} from '@/features/stats/api/useStats'
import {Button} from '@/shared/ui/button'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
import {Loader} from '@/shared/ui/loader'

export default function ProfilePage() {
  const navigate = useNavigate()
  const user = useUserStore(s => s.user)
  const logout = useUserStore(s => s.logout)
  const {data: stats, isLoading} = useAuthorStats()

  if (!user) return null

  const s = (stats as any)?.data

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Профиль</h1>
      <Card>
        <CardContent className="p-4 space-y-1">
          <p><strong>Email:</strong> {user.email}</p>
          <p><strong>Имя:</strong> {user.first_name} {user.last_name}</p>
          {user.username && <p><strong>Логин:</strong> {user.username}</p>}
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>Статистика автора</CardTitle></CardHeader>
        <CardContent className="p-4 grid grid-cols-2 gap-4">
          {isLoading ? <Loader /> : (
            <>
              <div><p className="text-2xl font-bold">{s?.total_tests || 0}</p><p className="text-sm text-muted-foreground">Тестов</p></div>
              <div><p className="text-2xl font-bold">{s?.total_attempts_received || 0}</p><p className="text-sm text-muted-foreground">Попыток</p></div>
              <div><p className="text-2xl font-bold">{s?.public_tests || 0}</p><p className="text-sm text-muted-foreground">Публичных</p></div>
              <div><p className="text-2xl font-bold">{s?.completed_attempts_received || 0}</p><p className="text-sm text-muted-foreground">Завершено</p></div>
            </>
          )}
        </CardContent>
      </Card>

      <Button variant="outline" onClick={() => {logout(); navigate('/login')}}>Выйти</Button>
    </div>
  )
}
