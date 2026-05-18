import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/shared/ui/button'

interface BackButtonProps {
  to?: string
  label?: string
  onClick?: () => void
}

export function BackButton({ to, label = 'Назад', onClick }: BackButtonProps) {
  return (
    <Button
      variant="outline"
      onClick={onClick}
      className="gap-2"
    >
      <ArrowLeft className="w-4 h-4" />
      {to ? (
        <Link to={to} className="contents">
          {label}
        </Link>
      ) : (
        label
      )}
    </Button>
  )
}
