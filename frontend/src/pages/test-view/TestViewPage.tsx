import { useMemo } from 'react'
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
  BarChart3,
  CheckCircle2,
  XCircle,
} from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'

import { useAuth } from '@/shared/hooks/useAuth'
import {
  getApiError } from '@/shared/lib/api-error'
import { formatDateTime } from '@/shared/lib/format'
import TypstRender from '@/shared/components/TypstRender'
import {
  client,
  getPublicTestApiV1CatalogTestIdGet,
  getTestApiV1TestsTestIdGet,
  getActiveAttemptApiV1AttemptsActiveGet,
  startAttemptApiV1AttemptsPost,
  getTestStatsApiV1StatsTestsTestIdGet,
  getScoreDistributionApiV1StatsTestsTestIdDistributionGet,
  getPerQuestionStatsApiV1StatsTestsTestIdPerQuestionGet,
  listTestAttemptsApiV1TestsTestIdAttemptsGet,
} from '@/shared/api'
import type {
  TestDetailResponse,
  TestAuthorDetailResponse,
  ActiveAttemptResponse,
  TestStatsResponse,
  ScoreDistributionResponse,
  PerQuestionStatsResponse,
  PerQuestionStat,
  AttemptAuthorSummary,
  PageAttemptAuthorSummary,
} from '@/shared/api'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { formatDate } from '@/shared/lib/format'

function ScoreDistributionChart({ testId }: { testId: number }) {
  const { data: distResponse } = useQuery({
    queryKey: ['score-distribution', testId],
    queryFn: () =>
      getScoreDistributionApiV1StatsTestsTestIdDistributionGet({ client, path: { test_id: testId } }),
    enabled: testId > 0,
  })
  const dist = distResponse?.data as ScoreDistributionResponse | undefined

  const distributionData = useMemo(() => {
    if (!dist) return []
    return [
      { label: '0-20%', count: dist.bucket_0_20 },
      { label: '20-40%', count: dist.bucket_20_40 },
      { label: '40-60%', count: dist.bucket_40_60 },
      { label: '60-80%', count: dist.bucket_60_80 },
      { label: '80-100%', count: dist.bucket_80_100 },
    ]
  }, [dist])

  if (!distributionData.length) {
    return <p className="text-sm text-muted-foreground py-8 text-center">No data yet</p>
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={distributionData} margin={{ top: 8, right: 8, bottom: 8, left: -16 }}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
          <Tooltip
            contentStyle={{ fontSize: 13, borderRadius: 8, border: '1px solid #e2e8f0' }}
            formatter={(value: number) => [value, 'attempts']}
          />
          <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

function RecentAttemptsTable({ testId }: { testId: number }) {
  const { data, isLoading } = useQuery({
    queryKey: ['test-attempts', testId],
    queryFn: () =>
      listTestAttemptsApiV1TestsTestIdAttemptsGet({
        client,
        path: { test_id: testId },
        query: { skip: 0, limit: 20 },
      }),
    enabled: testId > 0,
  })

  const attempts = (data?.data as PageAttemptAuthorSummary | undefined)?.items ?? []

  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border p-6 shadow-sm">
        <h3 className="text-sm font-semibold mb-4">Недавние попытки</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (attempts.length === 0) {
    return (
      <div className="bg-white rounded-xl border p-6 shadow-sm">
        <h3 className="text-sm font-semibold mb-4">Недавние попытки</h3>
        <p className="text-sm text-muted-foreground py-4 text-center">Нет попыток</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl border p-6 shadow-sm overflow-hidden">
      <h3 className="text-sm font-semibold mb-4">Недавние попытки</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2 font-medium text-muted-foreground">Пользователь</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Статус</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Результат</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Время</th>
              <th className="text-left py-2 font-medium text-muted-foreground">Дата</th>
            </tr>
          </thead>
          <tbody>
            {attempts.map((attempt) => (
              <tr key={attempt.id} className="border-b last:border-0 hover:bg-gray-50">
                <td className="py-3">{attempt.user_name}</td>
                <td className="py-3">
                  {attempt.status === 'completed' ? (
                    <span className="inline-flex items-center gap-1 text-green-600">
                      <CheckCircle2 className="w-4 h-4" />
                      Завершен
                    </span>
                  ) : attempt.status === 'in_progress' ? (
                    <span className="inline-flex items-center gap-1 text-blue-600">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      В процессе
                    </span>
                  ) : attempt.status === 'expired' ? (
                    <span className="inline-flex items-center gap-1 text-orange-600">
                      <XCircle className="w-4 h-4" />
                      Истекло время
                    </span>
                  ) : (
                    <span className="text-gray-600">{attempt.status}</span>
                  )}
                </td>
                <td className="py-3">
                  {attempt.score !== null && attempt.max_score !== null ? (
                    <span className="font-medium">
                      {attempt.score} / {attempt.max_score}
                    </span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </td>
                <td className="py-3">
                  {attempt.time_spent_minutes !== null ? (
                    <span>{attempt.time_spent_minutes} мин</span>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </td>
                <td className="py-3 text-muted-foreground">
                  {formatDateTime(attempt.started_at)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}


function QuestionsByCorrectness({ testId }: { testId: number }) {
  const { data: perQuestionResponse } = useQuery({
    queryKey: ['per-question-stats', testId],
    queryFn: () =>
      getPerQuestionStatsApiV1StatsTestsTestIdPerQuestionGet({ client, path: { test_id: testId } }),
    enabled: testId > 0,
  })
  const questions = (perQuestionResponse?.data as PerQuestionStatsResponse | undefined)?.items ?? []

  return (
    <div className="bg-white rounded-xl border p-6 shadow-sm">
      <h3 className="text-sm font-semibold mb-4">Вопросы по правильности</h3>
      {questions.length === 0 ? (
        <p className="text-sm text-muted-foreground py-4 text-center">No data yet</p>
      ) : (
        <div className="space-y-3">
          {questions.map((q, idx) => (
            <div key={q.question_id} className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground w-6 shrink-0">Q{idx + 1}</span>
              <span className="text-sm truncate flex-1">{q.question_text}</span>
              <span className="text-xs font-medium w-10 text-right">{q.correct_percent}%</span>
              <div className="w-32 h-3 bg-gray-100 rounded-full overflow-hidden shrink-0">
                <div
                  className={`h-full rounded-full transition-all ${
                    q.correct_percent >= 80
                      ? 'bg-green-500'
                      : q.correct_percent >= 50
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                  }`}
                  style={{ width: `${Math.min(q.correct_percent, 100)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
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
    queryKey: ['test', testId, user?.id],
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
            {test.author_name || `#${test.author_id}`}
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
          <TypstRender source={test.description} mode="preview" />
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

          {/* Score Distribution Chart */}
          <div className="bg-white rounded-xl border p-6 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <BarChart3 className="h-5 w-5 text-indigo-500" />
              <h3 className="text-sm font-semibold">Распределение баллов</h3>
            </div>
            <ScoreDistributionChart testId={id} />
          </div>

          {/* Questions by Correctness */}
          <QuestionsByCorrectness testId={id} />

          {/* Recent Attempts */}
          <RecentAttemptsTable testId={id} />
        </div>
      )}
    </div>
  )
}
