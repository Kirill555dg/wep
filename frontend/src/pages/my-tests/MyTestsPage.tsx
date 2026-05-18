import React, { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Pencil, Settings, Trash2, ListChecks } from 'lucide-react'
import {
  listMyTestsApiV1TestsGet,
  createTestApiV1TestsPost,
  deleteTestApiV1TestsTestIdDelete,
  client,
} from '@/shared/api'
import type { TestResponse } from '@/shared/api'
import { Badge } from '@/shared/ui/badge'
import { Button } from '@/shared/ui/button'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/shared/ui/dialog'
import { useAuth } from '@/shared/hooks/useAuth'
import { useToast } from '@/shared/hooks/useToast'
import { getApiError } from '@/shared/lib/api-error'

type FilterTab = 'all' | 'published' | 'private'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU')
}

function TestCard({
  test,
  onDelete,
}: {
  test: TestResponse
  onDelete: (id: number) => void
}) {
  return (
    <div className="group bg-white rounded-lg shadow-sm overflow-hidden hover:-translate-y-0.5 hover:shadow-md transition-all flex flex-col">
      <div className="h-48 w-full bg-gradient-to-br from-indigo-100 to-blue-50" />
      <div className="p-4 flex-1 flex flex-col">
        <Link
          to={`/tests/${test.id}/edit`}
          className="text-lg font-semibold truncate mb-2 hover:text-indigo-600 transition-colors"
        >
          {test.title || 'Без названия'}
        </Link>

        {test.tags && test.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {test.tags.map((tag) => (
              <Badge key={tag.id} variant="outline" className="text-xs">
                {tag.name}
              </Badge>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 mb-2 text-xs">
          <Badge
            variant={test.is_public ? 'success' : 'secondary'}
            className="text-xs"
          >
            {test.is_public ? '🟢 Опубликован' : '🔒 Приватный'}
          </Badge>
        </div>

        <div className="flex items-center gap-3 text-xs text-muted-foreground mb-4 flex-wrap">
          <span className="flex items-center gap-1">
            <ListChecks className="w-3.5 h-3.5" />
            {test.questions_count ?? 0} вопросов
          </span>
          <span>{formatDate(test.created_at)}</span>
        </div>

        <div className="mt-auto flex flex-wrap gap-2 pt-2 border-t border-gray-100">
          <Button variant="outline" size="sm" asChild className="flex-1">
            <Link to={`/tests/${test.id}/edit`}>
              <Pencil className="w-3.5 h-3.5 mr-1" />
              Редактировать
            </Link>
          </Button>
          <Button variant="outline" size="sm" asChild className="flex-1">
            <Link to={`/tests/${test.id}/settings`}>
              <Settings className="w-3.5 h-3.5 mr-1" />
              Настройки
            </Link>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
            onClick={() => onDelete(test.id)}
          >
            <Trash2 className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="h-48 bg-gray-200 animate-pulse" />
      <div className="p-4 space-y-3">
        <div className="h-5 bg-gray-200 rounded animate-pulse w-3/4" />
        <div className="flex gap-1">
          <div className="h-5 w-14 bg-gray-200 rounded-full animate-pulse" />
          <div className="h-5 w-16 bg-gray-200 rounded-full animate-pulse" />
        </div>
        <div className="h-3 bg-gray-200 rounded animate-pulse w-1/2" />
        <div className="h-8 bg-gray-200 rounded animate-pulse w-full mt-2" />
      </div>
    </div>
  )
}

export default function MyTestsPage() {
  const { isAuthed, requireAuth } = useAuth()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { error: showError } = useToast()
  const [filter, setFilter] = useState<FilterTab>('all')
  const [deleteId, setDeleteId] = useState<number | null>(null)

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

  const createMutation = useMutation({
    mutationFn: () =>
      createTestApiV1TestsPost({
        client,
        body: {
          title: '',
          is_public: false,
          attempt_limit: null,
          tag_names: [],
        },
      }),
    onSuccess: (res) => {
      navigate(`/tests/${res.data.id}/edit`)
    },
    onError: (err) => {
      const { message } = getApiError(err)
      showError(message)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) =>
      deleteTestApiV1TestsTestIdDelete({
        client,
        path: { test_id: id },
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-tests'] })
      setDeleteId(null)
    },
    onError: (err) => {
      const { message } = getApiError(err)
      showError(message)
      setDeleteId(null)
    },
  })

  const handleConfirmDelete = () => {
    if (deleteId !== null) {
      deleteMutation.mutate(deleteId)
    }
  }

  const isEmpty = filteredTests.length === 0 && !isLoading && !error

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
        <h1 className="text-2xl font-bold">Мои тесты</h1>
        <Button
          onClick={() => createMutation.mutate()}
          disabled={createMutation.isPending}
        >
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

      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      )}

      {error && (
        <div className="text-center py-16 text-red-600">
          <p className="mb-4">Ошибка загрузки</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Повторить
          </Button>
        </div>
      )}

      {isEmpty && (
        <div className="text-center py-16">
          <p className="text-gray-500 mb-4">
            У вас пока нет тестов. Создайте первый!
          </p>
          <Button onClick={() => createMutation.mutate()}>
            <Plus className="w-4 h-4 mr-1" />
            Создать тест
          </Button>
        </div>
      )}

      {!isLoading && !error && filteredTests.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {filteredTests.map((test) => (
            <TestCard key={test.id} test={test} onDelete={setDeleteId} />
          ))}
        </div>
      )}

      <Dialog open={deleteId !== null} onOpenChange={(open) => !open && setDeleteId(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить тест?</DialogTitle>
            <DialogDescription>
              Это действие нельзя отменить. Тест будет удален навсегда.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteId(null)}>
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={handleConfirmDelete}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Удаление...' : 'Удалить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
