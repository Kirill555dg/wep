import { useState, useEffect } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, Clock, ListChecks } from 'lucide-react'
import { searchCatalogApiV1CatalogGet, listTagsApiV1TagsGet, client } from '@/shared/api'
import type { TestResponse, TagResponse } from '@/shared/api'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'

function TestCard({
  test,
  onTagClick,
  onAuthorClick,
}: {
  test: TestResponse
  onTagClick: (slug: string) => void
  onAuthorClick: (authorId: number) => void
}) {
  const handleTagClick = (e: React.MouseEvent, slug: string) => {
    e.preventDefault()
    e.stopPropagation()
    onTagClick(slug)
  }

  const handleAuthorClick = (e: React.MouseEvent) => {
    e.preventDefault()
    e.stopPropagation()
    onAuthorClick(test.author_id)
  }

  return (
    <Link
      to={`/tests/${test.id}`}
      className="group block bg-white rounded-lg shadow-sm overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all"
    >
      <div className="h-48 w-full bg-gradient-to-br from-indigo-100 to-blue-50" />
      <div className="p-4">
        <h3 className="font-semibold text-base truncate mb-2">{test.title}</h3>
        {test.tags && test.tags.length > 0 && (
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
                    onTagClick(tag.slug)
                  }
                }}
              >
                <Badge
                  variant="default"
                  className="cursor-pointer select-none hover:bg-indigo-200 transition-colors"
                >
                  {tag.name}
                </Badge>
              </span>
            ))}
          </div>
        )}
        <div className="flex items-center gap-3 text-xs text-muted-foreground flex-wrap">
          <span
            role="button"
            tabIndex={0}
            className="cursor-pointer hover:underline"
            onClick={handleAuthorClick}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                onAuthorClick(test.author_id)
              }
            }}
          >
            Автор #{test.author_id}
          </span>
          <span className="flex items-center gap-1">
            <ListChecks className="w-3.5 h-3.5" />
            {test.questions_count ?? 0} вопросов
          </span>
          {test.time_limit_minutes && (
            <span className="flex items-center gap-1">
              <Clock className="w-3.5 h-3.5" />
              {test.time_limit_minutes} мин
            </span>
          )}
        </div>
      </div>
    </Link>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="h-48 bg-gray-200 animate-pulse" />
      <div className="p-4 space-y-3">
        <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
        <div className="flex gap-1">
          <div className="h-5 w-14 bg-gray-200 rounded-full animate-pulse" />
          <div className="h-5 w-16 bg-gray-200 rounded-full animate-pulse" />
        </div>
        <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
      </div>
    </div>
  )
}

export default function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [inputValue, setInputValue] = useState(searchParams.get('q') || '')

  const activeTags = searchParams.get('tags')?.split(',').filter(Boolean) || []
  const authorId = searchParams.get('authorId') || ''

  const debouncedQ = useDebouncedValue(inputValue, 300)

  useEffect(() => {
    const nextQ = debouncedQ.trim()
    setSearchParams((prev) => {
      const currentQ = prev.get('q') || ''
      if (currentQ === nextQ) return prev
      const next = new URLSearchParams(prev)
      if (nextQ) {
        next.set('q', nextQ)
      } else {
        next.delete('q')
      }
      return next
    }, { replace: true })
  }, [debouncedQ, setSearchParams])

  useEffect(() => {
    const urlQ = searchParams.get('q') || ''
    setInputValue((prev) => {
      if (prev === urlQ) return prev
      return urlQ
    })
  }, [searchParams])

  const { data: tagsResponse } = useQuery({
    queryKey: ['tags'],
    queryFn: () => listTagsApiV1TagsGet({ client }),
  })
  const tags: TagResponse[] = tagsResponse?.data || []

  const { data: catalogResponse, isLoading, error } = useQuery({
    queryKey: ['catalog', debouncedQ, activeTags.join(','), authorId],
    queryFn: () =>
      searchCatalogApiV1CatalogGet({
        client,
        query: {
          q: debouncedQ || undefined,
          tags: activeTags.length ? activeTags : undefined,
          skip: 0,
          limit: 20,
          ...(authorId ? { author_id: Number(authorId) } : {}),
        } as any,
      }),
  })
  const tests: TestResponse[] = catalogResponse?.data || []

  const toggleTag = (slug: string) => {
    const next = new URLSearchParams(searchParams)
    const current = next.get('tags')?.split(',').filter(Boolean) || []
    if (current.includes(slug)) {
      const updated = current.filter((s) => s !== slug)
      if (updated.length) {
        next.set('tags', updated.join(','))
      } else {
        next.delete('tags')
      }
    } else {
      next.set('tags', [...current, slug].join(','))
    }
    setSearchParams(next, { replace: true })
  }

  const resetTags = () => {
    const next = new URLSearchParams(searchParams)
    next.delete('tags')
    setSearchParams(next, { replace: true })
  }

  const setAuthorFilter = (id: number) => {
    const next = new URLSearchParams(searchParams)
    next.set('authorId', String(id))
    setSearchParams(next, { replace: true })
  }

  const resetFilters = () => {
    setSearchParams(new URLSearchParams(), { replace: true })
    setInputValue('')
  }

  const isEmpty = tests.length === 0 && !isLoading && !error

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="max-w-xl mx-auto mb-6 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="search"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Поиск тестов..."
          className="w-full h-10 pl-10 pr-4 rounded-md border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        />
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        <span
          role="button"
          tabIndex={0}
          onClick={resetTags}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault()
              resetTags()
            }
          }}
        >
          <Badge
            variant={activeTags.length === 0 ? 'default' : 'outline'}
            className="cursor-pointer select-none shrink-0"
          >
            Все
          </Badge>
        </span>
        {tags.map((tag) => (
          <span
            key={tag.id}
            role="button"
            tabIndex={0}
            onClick={() => toggleTag(tag.slug)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                toggleTag(tag.slug)
              }
            }}
          >
            <Badge
              variant={activeTags.includes(tag.slug) ? 'default' : 'outline'}
              className="cursor-pointer select-none shrink-0"
            >
              {tag.name}
            </Badge>
          </span>
        ))}
      </div>

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {Boolean(error) && (
        <div className="text-center py-16 text-red-600">
          <p className="mb-4">Ошибка загрузки</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Повторить
          </Button>
        </div>
      )}

      {isEmpty && (
        <div className="text-center py-16">
          <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">Нет тестов по заданному запросу</p>
          <Button variant="ghost" onClick={resetFilters}>
            Сбросить фильтры
          </Button>
        </div>
      )}

      {!isLoading && !error && tests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {tests.map((test) => (
            <TestCard
              key={test.id}
              test={test}
              onTagClick={toggleTag}
              onAuthorClick={setAuthorFilter}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function useDebouncedValue<T>(value: T, delay: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}
