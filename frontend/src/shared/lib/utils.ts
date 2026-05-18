import type { QuestionType } from '@/shared/api'
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function getQuestionTypeLabel(type: QuestionType): string {
  const labels: Record<QuestionType, string> = {
    SINGLE_CHOICE: 'Одиночный выбор',
    MULTIPLE_CHOICE: 'Множественный выбор',
    TEXT: 'Текстовый ответ',
    ESSAY: 'Эссе',
  }
  return labels[type] || type
}

export function getQuestionTypeIcon(type: QuestionType): string {
  const icons: Record<QuestionType, string> = {
    SINGLE_CHOICE: '🔘',
    MULTIPLE_CHOICE: '☑️',
    TEXT: '📝',
    ESSAY: '📄',
  }
  return icons[type] || '❓'
}

// Re-export formatting utilities for backward compatibility
export {
  formatTime,
  formatDateTime,
  calculateScore,
  formatDate,
  formatDateOnly,
  formatTimeSpent,
  formatDuration,
  formatScore,
  percent,
} from './format'

export function truncateText(text: string, maxLength: number = 100): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength).trim() + '...'
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null
  return (...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}
