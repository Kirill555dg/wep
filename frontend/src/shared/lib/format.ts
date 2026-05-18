/**
 * Unified formatting utilities for dates, times, scores, and numbers.
 * DRY principle: all formatting functions in one place.
 */

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('ru-RU')
}

export function formatDateTime(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatDateOnly(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  })
}

export function formatTime(seconds: number): string {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = seconds % 60

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`
  }
  return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`
}

export function formatTimeSpent(minutes: number | null): string {
  if (minutes === null || minutes === undefined) return '-'
  if (minutes < 1) return '< 1 мин'
  if (minutes < 60) return `${minutes} мин`
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (m === 0) return `${h} ч`
  return `${h} ч ${m} мин`
}

export function formatDuration(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  if (m === 0) return `${s}с`
  if (s === 0) return `${m}м`
  return `${m}м ${s}с`
}

export function formatScore(score: number, max: number): string {
  const pct = max > 0 ? Math.round((score / max) * 100) : 0
  return `${score} / ${max} (${pct}%)`
}

export function calculateScore(earned: number, max: number): number {
  if (max === 0) return 0
  return Math.round((earned / max) * 100)
}

export function percent(score: number | null, max: number | null): number | null {
  if (score === null || max === null || max === 0) return null
  return Math.round((score / max) * 100)
}
