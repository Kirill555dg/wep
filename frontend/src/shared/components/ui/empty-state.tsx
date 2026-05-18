import { Package, Search } from 'lucide-react'
import { cn } from '@/shared/lib/utils'

interface EmptyStateProps {
  icon?: 'package' | 'search'
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({ icon = 'package', title, description, action, className }: EmptyStateProps) {
  const Icon = icon === 'search' ? Search : Package

  return (
    <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
      <div className="w-16 h-16 rounded-full bg-gray-50 flex items-center justify-center mb-4">
        <Icon className="w-8 h-8 text-gray-400" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      {description && <p className="text-sm text-gray-600 mb-4 max-w-md">{description}</p>}
      {action && <div className="flex gap-2">{action}</div>}
    </div>
  )
}
