import { useState, useEffect, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ChevronLeft, ChevronRight, Clock, Eye, CalendarDays, X } from 'lucide-react'

import { useAuth } from '@/shared/hooks/useAuth'
import { getApiError } from '@/shared/lib/api-error'
import {
  listMyAttemptsApiV1AttemptsGet,
  getCalendarApiV1StatsCalendarGet,
  client,
} from '@/shared/api'
import type { AttemptSummary, CalendarResponse } from '@/shared/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/shared/ui/tabs'

function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDateOnly(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

function formatTimeSpent(minutes: number | null): string {
  if (minutes === null || minutes === undefined) return '-'
  if (minutes < 1) return '< 1 мин'
  if (minutes < 60) return `${minutes} мин`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (m === 0) return `${h} ч`
  return `${h} ч ${m} мин`
}

function getAttemptDateKey(startedAt: string): string {
  return startedAt.slice(0, 10)
}

function percent(score: number | null, max: number | null): number | null {
  if (score === null || max === null || max === 0) return null
  return Math.round((score / max) * 100)
}

function cellBg(count: number): string {
  if (count === 0) return 'bg-gray-100'
  if (count === 1) return 'bg-green-200'
  if (count <= 3) return 'bg-green-400'
  return 'bg-green-600'
}

function statusVariant(status: string): 'default' | 'secondary' | 'destructive' | 'success' | 'warning' | 'outline' {
  if (status === 'completed') return 'success'
  if (status === 'expired') return 'warning'
  return 'secondary'
}

function statusLabel(status: string): string {
  if (status === 'completed') return 'Завершен'
  if (status === 'expired') return 'Просрочен'
  if (status === 'in_progress') return 'В процессе'
  return status
}

function buildCalendarGrid(year: number, month: number, days: CalendarResponse['days']) {
  const daysInMonth = new Date(year, month, 0).getDate()
  const firstDayOfWeek = new Date(year, month - 1, 1).getDay()
  const mondayOffset = firstDayOfWeek === 0 ? 6 : firstDayOfWeek - 1
  const totalCells = mondayOffset + daysInMonth
  const rows = Math.ceil(totalCells / 7)
  const cells: Array<{ day: number | null; count: number; dateKey: string | null }> = []

  for (let i = 0; i < mondayOffset; i++) {
    cells.push({ day: null, count: 0, dateKey: null })
  }
  for (let day = 1; day <= daysInMonth; day++) {
    const dateKey = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`
    cells.push({ day, count: days?.[dateKey] ?? 0, dateKey })
  }
  const remaining = rows * 7 - cells.length
  for (let i = 0; i < remaining; i++) {
    cells.push({ day: null, count: 0, dateKey: null })
  }
  return cells
}

export default function HistoryPage() {
  const { isAuthed } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthed) {
      navigate('/login?redirect=/history')
    }
  }, [isAuthed, navigate])

  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [calendarDate, setCalendarDate] = useState(new Date())
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'expired'>('all')

  const {
    data: recentAttempts,
    error: recentError,
  } = useQuery({
    queryKey: ['my-attempts'],
    queryFn: () => listMyAttemptsApiV1AttemptsGet({ client, query: { limit: 1 } }),
  })

  const {
    data: allAttemptsPage,
    error: listError,
  } = useQuery({
    queryKey: ['my-attempts', 'list'],
    queryFn: () => listMyAttemptsApiV1AttemptsGet({ client, query: { skip: 0, limit: 100 } }),
  })

  const year = calendarDate.getFullYear()
  const month = calendarDate.getMonth() + 1

  const {
    data: calendarResponse,
    error: calendarError,
  } = useQuery({
    queryKey: ['calendar', year, month],
    queryFn: () => getCalendarApiV1StatsCalendarGet({ client, query: { year, month } }),
  })

  useEffect(() => {
    if (recentError) toast.error(getApiError(recentError).message)
    if (listError) toast.error(getApiError(listError).message)
    if (calendarError) toast.error(getApiError(calendarError).message)
  }, [recentError, listError, calendarError])

  const recentAttempt = recentAttempts?.data?.items?.[0] ?? null
  const allAttempts = allAttemptsPage?.data?.items ?? []

  const filteredAttempts = useMemo(() => {
    let result = allAttempts
    if (statusFilter !== 'all') {
      result = result.filter((a) => a.status === statusFilter)
    }
    if (selectedDate) {
      result = result.filter((a) => getAttemptDateKey(a.started_at) === selectedDate)
    }
    return result
  }, [allAttempts, statusFilter, selectedDate])

  const handlePrevMonth = () => {
    setCalendarDate((prev) => {
      const d = new Date(prev)
      d.setMonth(d.getMonth() - 1)
      return d
    })
  }

  const handleNextMonth = () => {
    setCalendarDate((prev) => {
      const d = new Date(prev)
      d.setMonth(d.getMonth() + 1)
      return d
    })
  }

  const calendarGrid = useMemo(() => {
    return buildCalendarGrid(year, month, calendarResponse?.data?.days ?? {})
  }, [year, month, calendarResponse])

  return (
    <div className="max-w-5xl mx-auto p-4 space-y-8">
      <h1 className="text-2xl font-bold">История</h1>

      {/* Recent Test */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Последний тест</h2>
        {recentAttempt ? (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-xl">
                <Link to={`/tests/${recentAttempt.test_id}`} className="hover:underline">
                  {recentAttempt.test_title}
                </Link>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex items-center gap-4 flex-wrap">
                <div className="text-lg font-medium">
                  {recentAttempt.score ?? 0} / {recentAttempt.max_score ?? 0}
                  {percent(recentAttempt.score, recentAttempt.max_score) !== null && (
                    <span className="text-muted-foreground ml-2">
                      ({percent(recentAttempt.score, recentAttempt.max_score)}%)
                    </span>
                  )}
                </div>
                {recentAttempt.status && (
                  <Badge variant={statusVariant(recentAttempt.status)}>
                    {statusLabel(recentAttempt.status)}
                  </Badge>
                )}
              </div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                {formatTimeSpent(recentAttempt.time_spent_minutes)}
              </div>
              <div className="text-sm text-muted-foreground">
                {formatDateTime(recentAttempt.started_at)}
              </div>
              <div className="pt-2">
                <Button asChild>
                  <Link to={`/attempts/${recentAttempt.id}`}>
                    <Eye className="h-4 w-4 mr-2" />
                    Смотреть результаты
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-8 text-center space-y-4">
              <p className="text-muted-foreground">Пока нет попыток. Пройдите тест из каталога!</p>
              <Button asChild variant="outline">
                <Link to="/catalog">Перейти в каталог</Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </section>

      {/* Activity Calendar */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold">Календарь активности</h2>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon" onClick={handlePrevMonth}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <span className="text-sm font-medium w-32 text-center capitalize">
              {calendarDate.toLocaleDateString('ru-RU', { month: 'long', year: 'numeric' })}
            </span>
            <Button variant="ghost" size="icon" onClick={handleNextMonth}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <Card>
          <CardContent className="pt-6">
            <div className="grid grid-cols-7 gap-2 text-center text-xs text-muted-foreground mb-2">
              <div>Пн</div>
              <div>Вт</div>
              <div>Ср</div>
              <div>Чт</div>
              <div>Пт</div>
              <div>Сб</div>
              <div>Вс</div>
            </div>
            <div className="grid grid-cols-7 gap-2">
              {calendarGrid.map((cell, index) => (
                <div
                  key={index}
                  className={[
                    'h-8 w-8 rounded-sm flex items-center justify-center text-xs transition-colors',
                    cell.day === null ? 'invisible' : '',
                    cell.day !== null ? cellBg(cell.count) : '',
                    cell.day !== null && cell.count >= 4 ? 'text-white' : 'text-foreground',
                    cell.dateKey && selectedDate === cell.dateKey ? 'ring-2 ring-primary ring-offset-1' : '',
                    cell.dateKey ? 'cursor-pointer hover:opacity-80' : '',
                  ].join(' ')}
                  title={
                    cell.dateKey
                      ? `${cell.dateKey}: ${cell.count} ${cell.count === 1 ? 'попытка' : 'попыток'}`
                      : undefined
                  }
                  onClick={() => cell.dateKey && setSelectedDate(cell.dateKey)}
                >
                  {cell.day}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </section>

      {/* Attempt List */}
      <section>
        <h2 className="text-lg font-semibold mb-3">Все попытки</h2>
        <Tabs value={statusFilter} onValueChange={(v) => setStatusFilter(v as typeof statusFilter)}>
          <TabsList className="mb-4">
            <TabsTrigger value="all">Все</TabsTrigger>
            <TabsTrigger value="completed">Завершенные</TabsTrigger>
            <TabsTrigger value="expired">Просроченные</TabsTrigger>
          </TabsList>
        </Tabs>

        {selectedDate && (
          <div className="flex items-center gap-2 mb-3">
            <CalendarDays className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">{selectedDate}</span>
            <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => setSelectedDate(null)}>
              <X className="h-3 w-3 mr-1" />
              Сбросить
            </Button>
          </div>
        )}

        <div className="space-y-2">
          {filteredAttempts.length === 0 ? (
            <p className="text-muted-foreground text-sm text-center py-6">Нет попыток</p>
          ) : (
            filteredAttempts.map((attempt) => (
              <div
                key={attempt.id}
                className="flex items-center justify-between rounded-lg border p-3 hover:bg-muted/50 transition-colors"
              >
                <div className="flex-1 space-y-1 min-w-0">
                  <Link to={`/tests/${attempt.test_id}`} className="font-medium hover:underline truncate block">
                    {attempt.test_title}
                  </Link>
                  <div className="flex items-center gap-3 text-sm text-muted-foreground flex-wrap">
                    <span>{formatDateOnly(attempt.started_at)}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {formatTimeSpent(attempt.time_spent_minutes)}
                    </span>
                    {attempt.status && (
                      <Badge variant={statusVariant(attempt.status)} className="text-[10px] px-1.5 py-0">
                        {statusLabel(attempt.status)}
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3 ml-4 shrink-0">
                  <div className="text-sm font-medium text-right">
                    {attempt.score ?? 0} / {attempt.max_score ?? 0}
                    {percent(attempt.score, attempt.max_score) !== null && (
                      <div className="text-xs text-muted-foreground">
                        {percent(attempt.score, attempt.max_score)}%
                      </div>
                    )}
                  </div>
                  <Button size="sm" variant="outline" asChild>
                    <Link to={`/attempts/${attempt.id}`}>
                      <Eye className="h-4 w-4 mr-1" />
                      Смотреть
                    </Link>
                  </Button>
                </div>
              </div>
            ))
          )}
        </div>
      </section>
    </div>
  )
}
