import { useParams, useNavigate } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import {
  ArrowLeft,
  Clock,
  ListChecks,
  Lock,
  Globe,
  Edit,
  Settings,
  Play,
  RotateCcw,
  LogIn,
  Loader2,
} from 'lucide-react'

import { useAuth } from '@/shared/hooks/useAuth'
import { getApiError } from '@/shared/lib/api-error'
import {
  client,
  getPublicTestApiV1CatalogTestIdGet,
  getTestApiV1TestsTestIdGet,
  getActiveAttemptApiV1AttemptsActiveGet,
  startAttemptApiV1AttemptsPost,
  getTestStatsApiV1StatsTestsTestIdGet,
} from '@/shared/api'
import type {
  TestDetailResponse,
  TestAuthorDetailResponse,
  ActiveAttemptResponse,
  TestStatsResponse,
} from '@/shared/api'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU')
}

export default function TestViewPage() {
  const { testId } = useParams<{ testId: string }>()
  const navigate = useNavigate()
  const { isAuthed, user } = useAuth()
  const id = Number(testId)

  const {
    data: testResponse,
    isLoading: testLoading,
  } = useQuery({
    queryKey: ['test', testId],
    queryFn: () => getPublicTestApiV1CatalogTestIdGet({ client, path: { test_id: id } }),
    enabled: !Number.isNaN(id),
  })

  const test = testResponse?.data as TestDetailResponse | undefined

  const isAuthor = isAuthed && user != null && test != null && user.id === test.author_id

  const { data: authorDetailResponse } = useQuery({
    queryKey: ['test-author', testId],
    queryFn: () => getTestApiV1TestsTestIdGet({ client, path: { test_id: id } }),
    enabled: isAuthor,
  })

  const authorDetail = authorDetailResponse?.data as TestAuthorDetailResponse | undefined

  const { data: activeAttemptResponse } = useQuery({
    queryKey: ['active-attempt', testId],
    queryFn: () => getActiveAttemptApiV1AttemptsActiveGet({ client, query: { test_id: id } }),
    enabled: isAuthed && !Number.isNaN(id),
  })

  const activeAttempt = activeAttemptResponse?.data as ActiveAttemptResponse | undefined

  const { data: statsResponse } = useQuery({
    queryKey: ['test-stats', testId],
    queryFn: () => getTestStatsApiV1StatsTestsTestIdGet({ client, path: { test_id: id } }),
    enabled: isAuthor,
  })

  const stats = statsResponse?.data as TestStatsResponse | undefined

  const startMutation = useMutation({
    mutationFn: () => startAttemptApiV1AttemptsPost({ client, body: { test_id: id } }),
    onSuccess: (res) => {
      if ((res as Record<string, unknown>).error) {
        const { message } = getApiError(res)
        toast.error(message)
      } else {
        navigate(`/tests/${testId}/take`)
      }
    },
    onError: (err) => {
      const { message } = getApiError(err)
      toast.error(message)
    },
  })

  if (Number.isNaN(id)) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-6">
        <p>Некорректный ID теста</p>
      </div>
    )
  }

  if (testResponse?.error != null) {
    const { message } = getApiError(testResponse)
    return (
      <div className="max-w-4xl mx-auto px-4 py-6">
        <p className="text-red-600 mb-4">{message}</p>
        <Button variant="outline" onClick={() => navigate('/catalog')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Вернуться в каталог
        </Button>
      </div>
    )
  }

  if (testLoading || !test) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        <div className="h-64 w-full bg-gray-200 rounded-xl animate-pulse" />
        <div className="h-8 bg-gray-200 rounded animate-pulse w-2/3" />
        <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
        <div className="h-32 bg-gray-200 rounded animate-pulse" />
        <div className="h-10 bg-gray-200 rounded animate-pulse w-40" />
      </div>
    )
  }

  const handleTagClick = (slug: string) => {
    navigate(`/catalog?tags=${slug}`)
  }

  const handleAuthorClick = () => {
    navigate(`/catalog?authorId=${test.author_id}`)
  }

  const attemptLimit = authorDetail?.attempt_limit ?? null

  const renderCta = () => {
    if (!isAuthed) {
      return (
        <Button variant="default" onClick={() => navigate(`/login?redirect=/tests/${testId}`)}>
          <LogIn className="w-4 h-4 mr-2" />
          Войти чтобы пройти
        </Button>
      )
    }

    if (activeAttempt?.has_active) {
      return (
        <Button variant="default" onClick={() => navigate(`/tests/${testId}/take`)}>
          <Play className="w-4 h-4 mr-2" />
          Продолжить тест
        </Button>
      )
    }

    const used = activeAttempt?.attempts_used ?? 0
    const hasLimit = attemptLimit != null
    const limitReached = hasLimit && used >= attemptLimit

    if (limitReached) {
      return (
        <Button variant="default" disabled>
          Лимит попыток исчерпан
        </Button>
      )
    }

    const label = used > 0 ? 'Пройти снова' : 'Начать тест'
    const Icon = used > 0 ? RotateCcw : Play

    return (
      <Button
        variant="default"
        onClick={() => startMutation.mutate()}
        disabled={startMutation.isPending}
      >
        {startMutation.isPending ? (
          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
        ) : (
          <Icon className="w-4 h-4 mr-2" />
        )}
        {label}
      </Button>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
      <button
        onClick={() => navigate('/catalog')}
        className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Вернуться в каталог
      </button>

      {/* Cover */}
      <div className="h-64 w-full bg-gradient-to-br from-indigo-100 to-blue-50 rounded-xl flex items-center justify-center">
        <span className="text-indigo-300 text-4xl font-bold">
          {test.title.slice(0, 2).toUpperCase()}
        </span>
      </div>

      {/* Title + tags */}
      <div>
        <h1 className="text-3xl font-bold mb-3">{test.title}</h1>
        {test.tags && test.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-3">
            {test.tags.map((tag) => (
              <button key={tag.id} onClick={() => handleTagClick(tag.slug)}>
                <Badge
                  variant="default"
                  className="cursor-pointer select-none hover:bg-indigo-200 transition-colors"
                >
                  {tag.name}
                </Badge>
              </button>
            ))}
          </div>
        )}
        <div className="text-sm text-muted-foreground">
          Автор{' '}
          <button
            onClick={handleAuthorClick}
            className="hover:underline text-foreground font-medium"
          >
            #{test.author_id}
          </button>
          {' • '}
          Создан {formatDate(test.created_at)}
        </div>
      </div>

      {/* Meta bar */}
      <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
        <span className="flex items-center gap-1">
          <ListChecks className="w-4 h-4" />
          {test.questions_count ?? 0} вопросов
        </span>
        {test.track_time && test.time_limit_minutes != null && (
          <span className="flex items-center gap-1">
            <Clock className="w-4 h-4" />
            {test.time_limit_minutes} мин
          </span>
        )}
        {isAuthor && attemptLimit != null && (
          <span className="flex items-center gap-1">
            Попытки: {activeAttempt?.attempts_used ?? 0}/{attemptLimit}
          </span>
        )}
        <span className="flex items-center gap-1">
          {test.is_public ? <Globe className="w-4 h-4" /> : <Lock className="w-4 h-4" />}
          {test.is_public ? 'Публичный' : 'Приватный'}
        </span>
        {test.track_time && (
          <span className="flex items-center gap-1 text-orange-600">
            <Clock className="w-4 h-4" />
            С учетом времени
          </span>
        )}
      </div>

      {/* Description */}
      {test.description && (
        <div className="bg-white rounded-xl border p-6 shadow-sm">
          <h2 className="text-lg font-semibold mb-2">Описание</h2>
          {test.description.includes('$') ? (
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono">
                {test.description}
              </pre>
            </div>
          ) : (
            <p className="text-base leading-relaxed text-gray-700 whitespace-pre-wrap">
              {test.description}
            </p>
          )}
        </div>
      )}

      {/* CTA + Author controls */}
      <div className="flex items-center gap-3 flex-wrap">
        {renderCta()}
        {isAuthor && (
          <>
            <Button variant="outline" onClick={() => navigate(`/tests/${testId}/edit`)}>
              <Edit className="w-4 h-4 mr-2" />
              Редактировать
            </Button>
            <Button variant="outline" onClick={() => navigate(`/tests/${testId}/settings`)}>
              <Settings className="w-4 h-4 mr-2" />
              Настройки
            </Button>
          </>
        )}
      </div>

      {/* Author stats */}
      {isAuthor && stats && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Статистика</h2>
          <div className="flex flex-wrap gap-4">
            <Card className="w-40">
              <CardHeader className="pb-2">
                <CardTitle className="text-2xl font-bold">{stats.total_attempts}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Всего попыток</p>
              </CardContent>
            </Card>
            <Card className="w-40">
              <CardHeader className="pb-2">
                <CardTitle className="text-2xl font-bold">{stats.completed_attempts}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Завершено</p>
              </CardContent>
            </Card>
            <Card className="w-40">
              <CardHeader className="pb-2">
                <CardTitle className="text-2xl font-bold">
                  {stats.avg_score_percent != null ? `${Math.round(stats.avg_score_percent)}%` : '—'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">Средний результат</p>
              </CardContent>
            </Card>
            {stats.avg_score != null && (
              <Card className="w-40">
                <CardHeader className="pb-2">
                  <CardTitle className="text-2xl font-bold">
                    {Number(stats.avg_score).toFixed(1)}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Средний балл</p>
                </CardContent>
              </Card>
            )}
          </div>

          {stats.avg_score_percent != null && (
            <div className="bg-white rounded-xl border p-6 shadow-sm">
              <h3 className="text-sm font-semibold mb-3">Распределение среднего результата</h3>
              <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                <div
                  className="bg-indigo-500 h-full rounded-full transition-all"
                  style={{ width: `${Math.min(stats.avg_score_percent, 100)}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                {Math.round(stats.avg_score_percent)}%
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
