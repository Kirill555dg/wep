/**
 * Attempt cache — localStorage-backed state for test taking.
 * Every answer change is persisted so the user can close and resume later.
 */
import { useCallback, useEffect } from 'react'

const LS_KEY = (testId: string) => `wep_attempt_${testId}`

export interface CachedAnswer {
  questionId: string
  type: string
  value: unknown
  answeredAt: string
}

export interface AttemptCache {
  attemptId: string | null
  testId: string
  currentIndex: number
  answers: Record<string, CachedAnswer>
  startedAt: string
}

export function useAttemptCache(testId: string) {
  const key = LS_KEY(testId)

  const load = useCallback((): AttemptCache | null => {
    try {
      const raw = localStorage.getItem(key)
      return raw ? JSON.parse(raw) : null
    } catch {
      return null
    }
  }, [key])

  const save = useCallback(
    (cache: AttemptCache) => {
      localStorage.setItem(key, JSON.stringify(cache))
    },
    [key],
  )

  const clear = useCallback(() => {
    localStorage.removeItem(key)
  }, [key])

  const updateAnswer = useCallback(
    (questionId: string, type: string, value: unknown) => {
      const current = load() || {
        attemptId: null,
        testId,
        currentIndex: 0,
        answers: {},
        startedAt: new Date().toISOString(),
      }
      current.answers[questionId] = {
        questionId,
        type,
        value,
        answeredAt: new Date().toISOString(),
      }
      save(current)
    },
    [load, save, testId],
  )

  return { load, save, clear, updateAnswer }
}
