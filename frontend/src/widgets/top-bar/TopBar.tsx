import { Link, useLocation } from 'react-router-dom'
import { useUserStore } from '@/entities/user/model/store'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/shared/ui/dropdown-menu'
import { Button } from '@/shared/ui/button'
import { LogOut, User, BookOpen, History } from 'lucide-react'

export function TopBar() {
  const location = useLocation()
  const user = useUserStore((s) => s.user)
  const token = useUserStore((s) => s.token)
  const logout = useUserStore((s) => s.logout)

  const isPublic = !token

  return (
    <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-12">
          {/* Logo */}
          <Link
            to="/catalog"
            className="flex items-center gap-1.5 text-sm font-semibold tracking-tight text-gray-900"
          >
            📐 <span>WEP</span>
          </Link>

          {/* Nav */}
          {!isPublic && (
            <nav className="hidden md:flex items-center gap-1">
              <TopBarLink to="/my-tests" active={location.pathname === '/my-tests'}>
                <BookOpen className="w-3.5 h-3.5" />
                My Tests
              </TopBarLink>
              <TopBarLink to="/history" active={location.pathname === '/history'}>
                <History className="w-3.5 h-3.5" />
                History
              </TopBarLink>
            </nav>
          )}

          {/* User / Login */}
          <div className="flex items-center">
            {isPublic ? (
              <Button asChild variant="ghost" size="sm" className="h-8 text-xs">
                <Link to="/login">Login</Link>
              </Button>
            ) : (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-1.5 outline-none px-2 py-1 rounded-md hover:bg-gray-100 transition-colors">
                    <User className="w-4 h-4 text-gray-500" />
                    <span className="text-xs font-medium text-gray-700 hidden sm:inline max-w-[88px] truncate">
                      {user?.first_name ?? 'User'}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-40">
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="flex items-center gap-2 text-xs cursor-pointer">
                      <User className="w-3.5 h-3.5" />
                      Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={logout}
                    className="text-red-600 focus:text-red-600 flex items-center gap-2 text-xs cursor-pointer"
                  >
                    <LogOut className="w-3.5 h-3.5" />
                    Sign out
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

function TopBarLink({
  to,
  active,
  children,
}: {
  to: string
  active: boolean
  children: React.ReactNode
}) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
        active
          ? 'bg-accent text-accent-foreground'
          : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
      }`}
    >
      {children}
    </Link>
  )
}
