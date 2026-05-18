import { Loader2 } from 'lucide-react'
import { cn } from '@/shared/lib/utils'

interface LoadingProps {
  message?: string
  className?: string
}

export function Loading({ message = 'Загрузка...', className }: LoadingProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 gap-4', className)}>
      <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      {message && <p className="text-sm text-gray-600">{message}</p>}
    </div>
  )
}

export function InlineLoading({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center justify-center py-8', className)}>
      <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
    </div>
  )
}
