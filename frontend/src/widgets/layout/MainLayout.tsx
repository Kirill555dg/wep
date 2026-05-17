import {ReactNode} from 'react'
import {Link, useNavigate} from 'react-router-dom'
import {useUserStore} from '@/entities/user/model/store'
import {Button} from '@/shared/ui/button'

export default function MainLayout({children}: {children: ReactNode}) {
  const user = useUserStore(s => s.user)
  const logout = useUserStore(s => s.logout)
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
        <Link to="/" className="font-bold text-lg">Test Constructor</Link>
        <nav className="flex items-center gap-4">
          {user ? (
            <>
              <Link to="/catalog" className="text-sm hover:underline">Каталог</Link>
              <Link to="/stats" className="text-sm hover:underline">Мои тесты</Link>
              <Link to="/profile" className="text-sm hover:underline">{user.first_name}</Link>
              <Button variant="ghost" size="sm" onClick={() => {logout(); navigate('/login')}}>Выйти</Button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-sm hover:underline">Вход</Link>
              <Link to="/register" className="text-sm hover:underline">Регистрация</Link>
            </>
          )}
        </nav>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="bg-white border-t px-6 py-4 text-center text-sm text-muted-foreground">
        © 2025 Test Constructor
      </footer>
    </div>
  )
}
