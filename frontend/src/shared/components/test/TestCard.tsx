import { Link } from 'react-router-dom'
import { BookOpen, Clock, Globe, Lock } from 'lucide-react'
import { Badge } from '@/shared/ui/badge'
import type { TestResponse } from '@/shared/api'

export interface TestCardProps {
  test: TestResponse
  showTags?: boolean
  showMeta?: boolean
  showAuthor?: boolean
  compact?: boolean
  onTagClick?: (slug: string) => void
  onAuthorClick?: (login: string) => void
}

export function TestCard({
  test,
  showTags = true,
  showMeta = true,
  showAuthor = false,
  compact = false,
  onTagClick,
  onAuthorClick,
}: TestCardProps) {
  const handleTagClick = (e: React.MouseEvent, slug: string) => {
    if (!onTagClick) return
    e.preventDefault()
    e.stopPropagation()
    onTagClick(slug)
  }

  const handleAuthorClick = (e: React.MouseEvent) => {
    if (!onAuthorClick) return
    e.preventDefault()
    e.stopPropagation()
    onAuthorClick(test.author_login || '')
  }

  return (
    <Link
      to={`/tests/${test.id}`}
      className="block bg-white rounded-lg shadow-sm overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all"
    >
      <div className="h-48 w-full bg-gradient-to-br from-indigo-100 to-blue-50" />
      <div className={compact ? 'p-4' : 'p-5'}>
        <h3 className="font-semibold text-base truncate mb-2">{test.title || 'Без названия'}</h3>

        {showAuthor && (
          <div className="flex items-center text-sm text-gray-600 mb-2">
            <span
              role="button"
              tabIndex={0}
              className="cursor-pointer hover:underline"
              onClick={handleAuthorClick}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault()
                  if (onAuthorClick) onAuthorClick(test.author_login || '')
                }
              }}
            >
              {test.author_name || `#${test.author_id}`}
            </span>
          </div>
        )}

        {showTags && test.tags && test.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {test.tags.map((tag) => (
              <span
                key={tag.id}
                role="button"
                tabIndex={0}
                onClick={(e) => handleTagClick(e, tag.slug)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault()
                    if (onTagClick) onTagClick(tag.slug)
                  }
                }}
              >
                <Badge
                  variant="default"
                  className="cursor-pointer select-none hover:bg-indigo-200 transition-colors text-xs"
                >
                  {tag.name}
                </Badge>
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
          <span className="flex items-center gap-1">
            <BookOpen className="w-3.5 h-3.5" />
            {test.questions_count ?? 0} вопросов
          </span>
          {test.time_limit_minutes != null && (
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {test.time_limit_minutes} мин
            </span>
          )}
          <span className="flex items-center gap-1">
            {test.is_public ? <Globe className="w-3.5 h-3.5" /> : <Lock className="w-3.5 h-3.5" />}
            {test.is_public ? 'Публичный' : 'Приватный'}
          </span>
        </div>
      </div>
    </Link>
  )
}
