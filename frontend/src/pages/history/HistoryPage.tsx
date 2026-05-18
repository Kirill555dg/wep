import { useState, useEffect, useMemo, useCallback } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { toast } from 'react-hot-toast'
import { ChevronLeft, ChevronRight, Clock, Eye, CalendarDays, X, Loader2, TrendingUp, TrendingDown } from 'lucide-react'

import { useAuth } from '@/shared/hooks/useAuth'
import { getApiError } from '@/shared/lib/api-error'
import {
  listMyAttemptsApiV1AttemptsGet,
  getCalendarApiV1StatsCalendarGet,
  client,
} from '@/shared/api'
import type { AttemptSummary } from '@/shared/api'
import { Card, CardContent } from '@/shared/ui/card'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { Tabs, TabsList, TabsTrigger } from '@/shared/ui/tabs'
import { formatDateOnly, formatTimeSpent, percent } from '@/shared/lib/format'

function getAttemptDateKey(startedAt: string): string {
  return startedAt.slice(0, 10)
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

const DAYS_SHORT = ['Mon', '', 'Wed', '', 'Fri', '', '']

const MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

function buildYearGrid(year: number, allDays: Record<string, number>) {
  const startDate = new Date(year, 0, 1)
  const endDate = new Date(year, 11, 31)
  const startDay = startDate.getDay()
  const colOffset = startDay === 0 ? 6 : startDay - 1

  const grid: Array<{ dateKey: string | null; count: number }> = []
  const current = new Date(startDate)
  current.setDate(current.getDate() - colOffset)

  while (current <= endDate || grid.length % 7 !== 0) {
    const key = `${current.getFullYear()}-${String(current.getMonth() + 1).padStart(2, '0')}-${String(current.getDate()).padStart(2, '0')}`
    const inYear = current.getFullYear() === year
    grid.push({
      dateKey: inYear ? key : null,
      count: inYear ? (allDays[key] ?? 0) : 0,
    })
    current.setDate(current.getDate() + 1)
  }

  const cols = Math.ceil(grid.length / 7)
  const rows = 7
  const matrix: typeof grid = []
  for (let col = 0; col < cols; col++) {
    for (let row = 0; row < rows; row++) {
      const idx = row + col * rows
      if (idx < grid.length) {
        matrix[row * cols + col] = grid[idx]
      }
    }
  }

  const monthLabels: Array<{ col: number; label: string }> = []
  for (let m = 0; m < 12; m++) {
    const firstOfMonth = new Date(year, m, 1)
    const dayOffset = firstOfMonth.getDay() === 0 ? 6 : firstOfMonth.getDay() - 1
    const daysFromStart = Math.floor((firstOfMonth.getTime() - startDate.getTime()) / 86400000) + colOffset
    const totalCols = Math.floor((daysFromStart + dayOffset) / 7)
    monthLabels.push({ col: totalCols, label: MONTH_NAMES[m] })
  }

  return { cols, rows, matrix, monthLabels }
}

function YearCalendar({
  year,
  days,
  selectedDate,
  onSelect,
}: {
  year: number
  days: Record<string, number>
  selectedDate: string | null
  onSelect: (dateKey: string | null) => void
}) {
  const { cols, monthLabels, matrix } = useMemo(() => buildYearGrid(year, days), [year, days])

  return (
    <div className="overflow-x-auto">
      <div className="inline-flex flex-col gap-0.5" style={{ minWidth: cols * 14 + 40 }}>
        <div className="flex ml-10 text-[10px] text-muted-foreground">
          {monthLabels.map((m, i) => (
            <div
              key={i}
              className="text-left"
              style={{ width: (i < monthLabels.length - 1 ? monthLabels[i + 1].col - m.col : cols - m.col) * 14 }}
            >
              {m.label}
            </div>
          ))}
        </div>
        <div className="flex">
          <div className="flex flex-col gap-0.5 mr-1 text-[10px] text-muted-foreground leading-[14px]">
            {DAYS_SHORT.map((d, i) => (
              <span key={i} className="h-[14px] w-8 text-right pr-1">{d}</span>
            ))}
          </div>
          <div className="flex gap-0.5">
            {Array.from({ length: cols }).map((_, col) => (
              <div key={col} className="flex flex-col gap-0.5">
                {Array.from({ length: 7 }).map((_, row) => {
                  const cell = matrix[row * cols + col]
                  return (
                    <div
                      key={row}
                      className={`h-[14px] w-[14px] rounded-[2px] ${cell?.dateKey ? cellBg(cell.count) + ' cursor-pointer hover:ring-1 hover:ring-primary' : 'invisible'} ${cell?.dateKey && selectedDate === cell.dateKey ? 'ring-1 ring-primary ring-offset-[0.5px]' : ''}`}
                      title={cell?.dateKey ? `${cell.dateKey}: ${cell.count}` : undefined}
                      onClick={() => cell?.dateKey && onSelect(cell.dateKey === selectedDate ? null : cell.dateKey)}
                    />
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
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
  const [calendarYear, setCalendarYear] = useState(new Date().getFullYear())
  const [statusFilter, setStatusFilter] = useState<'all' | 'completed' | 'expired'>('all')

  const {
    data: recentAttempts,
    error: recentError,
  } = useQuery({
    queryKey: ['my-attempts'],
    queryFn: () => listMyAttemptsApiV1AttemptsGet({ client, query: { limit: 1 } }),
  })

  const [allAttempts, setAllAttempts] = useState<AttemptSummary[]>([])
  const [totalAttempts, setTotalAttempts] = useState(0)
  const [loadingMore, setLoadingMore] = useState(false)

  const {
    data: allAttemptsPage,
    error: listError,
  } = useQuery({
    queryKey: ['my-attempts', 'list', 'page1'],
    queryFn: () => listMyAttemptsApiV1AttemptsGet({ client, query: { skip: 0, limit: 20 } }),
  })

  useEffect(() => {
    if (allAttemptsPage?.data) {
      setAllAttempts(allAttemptsPage.data.items ?? [])
      setTotalAttempts(allAttemptsPage.data.total)
    }
  }, [allAttemptsPage])

  const loadMore = useCallback(async () => {
    if (loadingMore) return
    setLoadingMore(true)
    try {
      const res = await listMyAttemptsApiV1AttemptsGet({ client, query: { skip: allAttempts.length, limit: 20 } })
      const page = res.data
      if (page?.items) {
        setAllAttempts((prev) => [...prev, ...page.items])
      }
    } catch {
      toast.error('Failed to load more')
    } finally {
      setLoadingMore(false)
    }
  }, [allAttempts.length, loadingMore])

  const hasMore = allAttempts.length < totalAttempts

  const { data: calendarResponses, error: calendarError } = useQuery({
    queryKey: ['calendar', calendarYear],
    queryFn: async () => {
      const months = Array.from({ length: 12 }, (_, i) => i + 1)
      const results = await Promise.all(
        months.map((m) => getCalendarApiV1StatsCalendarGet({ client, query: { year: calendarYear, month: m } })),
      )
      const allDays: Record<string, number> = {}
      for (const res of results) {
        if (res.data?.days) {
          Object.assign(allDays, res.data.days)
        }
      }
      return allDays
    },
  })

  const yearDays = calendarResponses ?? {}

  useEffect(() => {
    if (recentError) toast.error(getApiError(recentError).message)
    if (listError) toast.error(getApiError(listError).message)
    if (calendarError) toast.error(getApiError(calendarError).message)
  }, [recentError, listError, calendarError])

  const recentAttempt = recentAttempts?.data?.items?.[0] ?? null

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

  const handlePrevYear = () => setCalendarYear((y) => y - 1)
  const handleNextYear = () => setCalendarYear((y) => y + 1)

  const last7DaysAvg = useMemo(() => {
    const now = new Date()
    const last7 = allAttempts.filter((a) => {
      const d = new Date(a.started_at)
      const diff = (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24)
      return diff <= 7 && a.status === 'completed' && a.score != null && a.max_score != null && a.max_score > 0
    })
    if (last7.length === 0) return null
    return last7.reduce((sum, a) => sum + (a.score! / a.max_score!) * 100, 0) / last7.length
  }, [allAttempts])

  const prev7DaysAvg = useMemo(() => {
    const now = new Date()
    const prev7 = allAttempts.filter((a) => {
      const d = new Date(a.started_at)
      const diff = (now.getTime() - d.getTime()) / (1000 * 60 * 60 * 24)
      return diff > 7 && diff <= 14 && a.status === 'completed' && a.score != null && a.max_score != null && a.max_score > 0
    })
    if (prev7.length === 0) return null
    return prev7.reduce((sum, a) => sum + (a.score! / a.max_score!) * 100, 0) / prev7.length
  }, [allAttempts])

  const trend = (() => {
    if (last7DaysAvg == null || prev7DaysAvg == null) return null
    const diff = last7DaysAvg - prev7DaysAvg
    return {
      value: Math.abs(diff).toFixed(1),
      direction: diff >= 0 ? ('up' as const) : ('down' as const),
      percent: prev7DaysAvg > 0 ? ((diff / prev7DaysAvg) * 100).toFixed(0) : '0',
    }
  })()

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">История</h1>
        {trend && (
          <div className="flex items-center gap-2 text-sm rounded-lg border px-3 py-1.5 bg-white">
            <span className="text-muted-foreground">За 7 дней:</span>
            <span className={`font-medium flex items-center gap-1 ${trend.direction === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {trend.direction === 'up' ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
              {trend.direction === 'up' ? '+' : ''}{trend.value}%
              <span className="text-xs text-muted-foreground">({trend.direction === 'up' ? '+' : ''}{trend.percent}%)</span>
            </span>
          </div>
        )}
      </div>

      {/* Top row: Recent Test + Calendar */}
      <div className="flex flex-col lg:flex-row gap-6">
        {/* Recent Test */}
        <div className="lg:w-80 shrink-0">
          <h2 className="text-lg font-semibold mb-3">Последний тест</h2>
          {recentAttempt ? (
            <Card>
              <CardContent className="p-5 space-y-3">
                <Link to={`/tests/${recentAttempt.test_id}`} className="font-semibold hover:underline block truncate">
                  {recentAttempt.test_title}
                </Link>
                <div className="flex items-center gap-3 flex-wrap">
                  <span className="text-lg font-medium">
                    {recentAttempt.score ?? 0}/{recentAttempt.max_score ?? 0}
                    {percent(recentAttempt.score, recentAttempt.max_score) !== null && (
                      <span className="text-muted-foreground ml-1 text-sm">
                        ({percent(recentAttempt.score, recentAttempt.max_score)}%)
                      </span>
                    )}
                  </span>
                  {recentAttempt.status && (
                    <Badge variant={statusVariant(recentAttempt.status)}>{statusLabel(recentAttempt.status)}</Badge>
                  )}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-3 w-3" />
                  {formatTimeSpent(recentAttempt.time_spent_minutes)}
                </div>
                <Button size="sm" asChild>
                  <Link to={`/attempts/${recentAttempt.id}`}>
                    <Eye className="h-4 w-4 mr-1" />
                    Смотреть
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="py-6 text-center space-y-3">
                <p className="text-sm text-muted-foreground">Пока нет попыток.</p>
                <Button size="sm" variant="outline" asChild>
                  <Link to="/catalog">Перейти в каталог</Link>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* GitHub-style Calendar */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-semibold">Активность</h2>
            <div className="flex items-center gap-1">
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handlePrevYear}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm font-medium w-20 text-center">{calendarYear}</span>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={handleNextYear}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <Card>
            <CardContent className="p-4">
              <YearCalendar
                year={calendarYear}
                days={yearDays}
                selectedDate={selectedDate}
                onSelect={setSelectedDate}
              />
            </CardContent>
          </Card>
        </div>
      </div>

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
          {hasMore && (
            <div className="flex justify-center pt-2">
              <Button variant="outline" onClick={loadMore} disabled={loadingMore}>
                {loadingMore ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                {loadingMore ? 'Loading...' : `Load more (${allAttempts.length}/${totalAttempts})`}
              </Button>
            </div>
          )}
        </div>
      </section>
    </div>
  )
}
