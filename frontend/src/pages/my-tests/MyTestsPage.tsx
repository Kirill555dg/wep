import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Plus } from 'lucide-react'
import { listMyTestsApiV1TestsGet, client } from '@/shared/api'
import type { TestResponse } from '@/shared/api'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/shared/hooks/useAuth'
import { TestCard } from '@/shared/components/test/TestCard'
import { SkeletonList } from '@/shared/components/ui/skeleton-card'
import { EmptyState } from '@/shared/components/ui/empty-state'

type FilterTab = 'all' | 'published' | 'private'

export default function MyTestsPage() {
  const { isAuthed, requireAuth } = useAuth()
  const navigate = useNavigate()
  const [filter, setFilter] = useState<FilterTab>('all')

  useEffect(() => {
    requireAuth('/my-tests')
  }, [requireAuth])

  const { data: testsResponse, isLoading, error } = useQuery({
    queryKey: ['my-tests'],
    queryFn: () => listMyTestsApiV1TestsGet({ client }),
    enabled: isAuthed,
  })

  const tests: TestResponse[] = testsResponse?.data ?? []

  const filteredTests = tests.filter((t) => {
    if (filter === 'published') return t.is_public
    if (filter === 'private') return !t.is_public
    return true
  })

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold">Мои тесты</h1>
        <Button onClick={() => navigate('/tests/new/edit')}>
          <Plus className="w-4 h-4 mr-1" />
          Новый тест
        </Button>
      </div>

      <div className="flex gap-2 mb-6">
        {([
          { key: 'all', label: 'Все' },
          { key: 'published', label: 'Опубликованные' },
          { key: 'private', label: 'Приватные' },
        ] as Array<{ key: FilterTab; label: string }>).map((tab) => (
          <Badge
            key={tab.key}
            variant={filter === tab.key ? 'default' : 'outline'}
            className="cursor-pointer select-none"
            onClick={() => setFilter(tab.key)}
          >
            {tab.label}
          </Badge>
        ))}
      </div>

      {isLoading && <SkeletonList count={4} />}

      {Boolean(error) && (
        <EmptyState
          icon="search"
          title="Ошибка загрузки"
          description="Не удалось загрузить список тестов"
          action={
            <Button variant="outline" onClick={() => window.location.reload()}>
              Повторить
            </Button>
          }
        />
      )}

      {filteredTests.length === 0 && !isLoading && !error && (
        <EmptyState
          title="Нет тестов"
          description="У вас пока нет тестов. Создайте первый!"
          action={
            <Button onClick={() => navigate('/tests/new/edit')}>
              <Plus className="w-4 h-4 mr-1" />
              Создать тест
            </Button>
          }
        />
      )}

      {filteredTests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
          {filteredTests.map((test) => (
            <TestCard key={test.id} test={test} showAuthor={false} />
          ))}
        </div>
      )}
    </div>
  )
}
