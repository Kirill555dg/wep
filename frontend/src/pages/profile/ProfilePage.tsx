import {useNavigate} from 'react-router-dom'
import {useUserStore} from '@/entities/user/model/store'
import {Button} from '@/shared/ui/button'

export default function ProfilePage() {
  const navigate = useNavigate()
  const user = useUserStore(s => s.user)
  const logout = useUserStore(s => s.logout)

  return (
    <div className="max-w-xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Профиль</h1>
      <p><strong>Email:</strong> {user?.email}</p>
      <p><strong>Имя:</strong> {user?.first_name} {user?.last_name}</p>
      <Button variant="outline" onClick={() => {logout(); navigate('/login')}}>Выйти</Button>
    </div>
  )
}
