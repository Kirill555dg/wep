import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useUserStore } from '@/entities/user/model/store'

export function useAuth() {
  const user = useUserStore((s) => s.user)
  const token = useUserStore((s) => s.token)
  const logout = useUserStore((s) => s.logout)
  const navigate = useNavigate()

  const isAuthed = !!token

  const requireAuth = useCallback(
    (redirectTo: string) => {
      if (!isAuthed) {
        navigate(`/login?redirect=${encodeURIComponent(redirectTo)}`)
        return false
      }
      return true
    },
    [isAuthed, navigate],
  )

  return { user, token, isAuthed, logout, requireAuth }
}
