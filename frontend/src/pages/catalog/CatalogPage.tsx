import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, User } from 'lucide-react'
import { searchCatalogApiV1CatalogGet, listTagsApiV1TagsGet, client, getCurrentUserProfileApiV1AuthMeGet } from '@/shared/api'
import type { TestResponse, TagResponse, UserResponse } from '@/shared/api'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { TestCard } from '@/shared/components/test/TestCard'
import { SkeletonList } from '@/shared/components/ui/skeleton-card'
import { EmptyState } from '@/shared/components/ui/empty-state'

export default function CatalogPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [inputValue, setInputValue] = useState(searchParams.get('q') || '')
  const [authorLogin, setAuthorLogin] = useState(searchParams.get('author_login') || '')

  const activeTags = searchParams.get('tags')?.split(',').filter(Boolean) || []

  const debouncedQ = useDebouncedValue(inputValue, 300)
  const debouncedAuthor = useDebouncedValue(authorLogin, 300)

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

  useEffect(() => {
    const urlAuthor = searchParams.get('author_login') || ''
    setAuthorLogin((prev) => {
      if (prev === urlAuthor) return prev
      return urlAuthor
    })
  }, [searchParams])

  const { data: tagsResponse } = useQuery({
    queryKey: ['tags'],
    queryFn: () => listTagsApiV1TagsGet({ client }),
  })
  const tags: TagResponse[] = tagsResponse?.data || []

  const { data: catalogResponse, isLoading, error } = useQuery({
    queryKey: ['catalog', debouncedQ, activeTags.join(','), debouncedAuthor],
    queryFn: () =>
      searchCatalogApiV1CatalogGet({
        client,
        query: {
          q: debouncedQ || undefined,
          tags: activeTags.length ? activeTags : undefined,
          skip: 0,
          limit: 20,
          ...(debouncedAuthor ? { author_login: debouncedAuthor } : {}),
        },
      }),
    enabled: true,
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

  const setAuthorFilter = (login: string) => {
    const next = new URLSearchParams(searchParams)
    if (login) {
      next.set('author_login', login)
    } else {
      next.delete('author_login')
    }
    setSearchParams(next, { replace: true })
  }

  const resetFilters = () => {
    setSearchParams(new URLSearchParams(), { replace: true })
    setInputValue('')
    setAuthorLogin('')
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="max-w-xl mx-auto mb-4 relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="search"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Поиск тестов..."
          className="w-full h-10 pl-10 pr-4 rounded-md border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
        />
      </div>

      {/* Author filter */}
      <div className="max-w-md mx-auto mb-4 flex gap-2">
        <div className="relative flex-1">
          <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={authorLogin}
            onChange={(e) => setAuthorLogin(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setAuthorFilter(authorLogin.trim())
              }
            }}
            placeholder="Фильтр по автору (логин)..."
            className="w-full h-10 pl-10 pr-24 rounded-md border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
          {debouncedAuthor && (
            <button
              onClick={() => {
                setAuthorLogin('')
                setAuthorFilter('')
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground hover:text-foreground"
            >
              Сбросить
            </button>
          )}
        </div>
        <Button
          size="sm"
          onClick={() => setAuthorFilter(authorLogin.trim())}
          disabled={!authorLogin.trim()}
        >
          Найти
        </Button>
      </div>

      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {debouncedAuthor && (
          <Badge variant="default" className="cursor-pointer select-none shrink-0 flex items-center gap-1">
            {debouncedAuthor}
            <button
              onClick={() => {
                setAuthorLogin('')
                setAuthorFilter('')
              }}
              className="ml-1 text-xs"
            >
              ×
            </button>
          </Badge>
        )}
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
            variant={activeTags.length === 0 && !debouncedAuthor ? 'default' : 'outline'}
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

      {isLoading && <SkeletonList count={6} />}

      {Boolean(error) && (
        <EmptyState
          icon="search"
          title="Ошибка загрузки"
          description="Не удалось загрузить каталог"
          action={
            <Button variant="outline" onClick={() => window.location.reload()}>
              Повторить
            </Button>
          }
        />
      )}

      {tests.length === 0 && !isLoading && !error && (
        <EmptyState
          icon="search"
          title="Нет тестов"
          description="Нет тестов по заданному запросу"
          action={
            <Button variant="ghost" onClick={resetFilters}>
              Сбросить фильтры
            </Button>
          }
        />
      )}

      {tests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {tests.map((test) => (
            <TestCard
              key={test.id}
              test={test}
              showAuthor
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
