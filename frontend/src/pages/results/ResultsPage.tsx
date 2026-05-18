import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ArrowLeft, Clock, AlertCircle } from 'lucide-react'

import { Button } from '@/shared/ui/button'
import { Loader } from '@/shared/ui/loader'
import { Badge } from '@/shared/ui/badge'
import {
  client,
  getResultApiV1AttemptsAttemptIdResultGet,
  getTestApiV1TestsTestIdGet,
} from '@/shared/api'
import type {
  AttemptResultResponse,
  TestDetailResponse,
  QuestionResponse,
} from '@/shared/api'

import QuestionPanel from '@/widgets/question-panel/QuestionPanel'
import TypstRender from '@/shared/components/TypstRender'
import MediaCarousel from '@/shared/components/MediaCarousel'
import AnswerBlocks from '@/shared/components/AnswerBlocks'

function formatDuration(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  if (m === 0) return `${s}с`
  if (s === 0) return `${m}м`
  return `${m}м ${s}с`
}

export default function ResultsPage() {
  const { attemptId } = useParams<{ attemptId: string }>()
  const navigate = useNavigate()
  const numAttemptId = Number(attemptId)
  const [currentIndex, setCurrentIndex] = useState(0)

  const {
    data: resultResponse,
    isLoading: resultLoading,
    error: resultError,
  } = useQuery({
    queryKey: ['attempt-result', attemptId],
    queryFn: () =>
      getResultApiV1AttemptsAttemptIdResultGet({
        client,
        path: { attempt_id: numAttemptId },
      }),
    enabled: !Number.isNaN(numAttemptId) && numAttemptId > 0,
  })

  const result = resultResponse?.data as AttemptResultResponse | undefined
  const testId = result?.test_id

  const { data: testResponse, isLoading: testLoading } = useQuery({
    queryKey: ['test-detail', testId],
    queryFn: () =>
      getTestApiV1TestsTestIdGet({ client, path: { test_id: testId! } }),
    enabled: !!testId,
  })

  const test = testResponse?.data as TestDetailResponse | undefined
  const testQuestions = test?.questions || []

  const isLoading = resultLoading || (testLoading && !!testId)

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Loader />
      </div>
    )
  }

  if (resultError || !result || Number.isNaN(numAttemptId) || numAttemptId <= 0) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Попытка не найдена</p>
        <Button asChild variant="outline">
          <Link to="/history">Вернуться к истории</Link>
        </Button>
      </div>
    )
  }

  const answers = result.answers || []

  if (!answers.length) {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Нет данных о попытке.</p>
        <Button asChild variant="outline">
          <Link to="/history">Вернуться к истории</Link>
        </Button>
      </div>
    )
  }

  const currentIdxSafe = Math.min(currentIndex, answers.length - 1)

  const questions: QuestionResponse[] = answers.map((a, idx) => {
    const tq = testQuestions.find((q) => q.id === a.question_id)
    if (tq) {
      return tq as QuestionResponse
    }
    return {
      id: a.question_id,
      question_type: a.question_type,
      text: a.question_text,
      order_number: idx + 1,
      points: a.points,
      image_url: null,
      options:
        a.correct_option_ids?.map((cid, i) => ({
          id: cid,
          text: `Option ${i + 1}`,
          order_number: i + 1,
        })) || [],
    }
  })

  const resultsMap: Record<
    string,
    { isCorrect: boolean; pointsEarned: number; maxPoints: number }
  > = {}
  answers.forEach((a) => {
    resultsMap[String(a.question_id)] = {
      isCorrect: a.is_correct ?? false,
      pointsEarned: a.points_earned ?? 0,
      maxPoints: a.points,
    }
  })

  const currentAnswer = answers[currentIdxSafe]
  const currentQuestion = questions[currentIdxSafe]

  const completionMessage =
    (result as any).completion_message ?? test?.completion_message ?? null

  const mediaFiles = currentQuestion?.image_url
    ? [
        {
          id: 'img-1',
          url: currentQuestion.image_url,
          type: 'image' as const,
          filename: 'image',
        },
      ]
    : []

  const reviewAnswerFor = (qid: number): unknown => {
    const ans = answers.find((a) => a.question_id === qid)
    if (!ans) return undefined
    if (ans.question_type === 'SINGLE_CHOICE') {
      return ans.selected_option_ids?.[0] ?? null
    }
    if (ans.question_type === 'MULTIPLE_CHOICE') {
      return ans.selected_option_ids ?? []
    }
    return ans.text_answer ?? ''
  }

  const reviewCorrectIdsFor = (qid: number): number[] => {
    return answers.find((a) => a.question_id === qid)?.correct_option_ids ?? []
  }

  const explanationFor = (qid: number): string | null => {
    return answers.find((a) => a.question_id === qid)?.explanation ?? null
  }

  const timeSpentSeconds = (() => {
    const started = result.started_at
      ? new Date(result.started_at).getTime()
      : 0
    const finished = result.finished_at
      ? new Date(result.finished_at).getTime()
      : Date.now()
    return Math.max(0, Math.floor((finished - started) / 1000))
  })()

  const correctCount = answers.filter((a) => a.is_correct === true).length

  const pointsBadgeText =
    (currentAnswer.points_earned || 0) > 0
      ? `+${currentAnswer.points_earned} балл${currentAnswer.points_earned === 1 ? '' : 'а'}`
      : '0 баллов'

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b h-12 shrink-0">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate('/history')}
          >
            <ArrowLeft className="h-4 w-4 mr-1" />
            Назад к истории
          </Button>
        </div>
        <h1 className="text-sm font-semibold">Результаты теста</h1>
        <Badge variant="outline" className="text-sm font-medium">
          {result.score} / {result.max_score} баллов
        </Badge>
      </div>

      {/* Body */}
      <div className="h-[calc(100vh-48px)] flex overflow-hidden">
        <div className="w-60 h-full flex flex-col bg-background overflow-hidden">
          <div className="flex-1 min-h-0">
            <QuestionPanel
              questions={questions}
              currentIndex={currentIdxSafe}
              onSelect={setCurrentIndex}
              mode="review"
              results={resultsMap}
            />
          </div>
          <div className="p-3 border-t space-y-2 text-sm shrink-0">
            <div className="flex justify-between font-medium">
              <span>Итого:</span>
              <span>
                {result.score}/{result.max_score}
              </span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Правильно:</span>
              <span>
                {correctCount}/{answers.length}
              </span>
            </div>
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1">
                <Clock className="h-4 w-4" />
                Время:
              </span>
              <span>{formatDuration(timeSpentSeconds)}</span>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-4 md:p-6">
          <div className="max-w-3xl mx-auto space-y-6">
            {completionMessage && (
              <div className="rounded-lg border p-4 bg-blue-50 text-blue-800 text-sm">
                <AlertCircle className="h-4 w-4 inline mr-2" />
                {completionMessage}
              </div>
            )}

            <div className="flex items-center gap-3">
              <span className="text-xs text-muted-foreground">
                Вопрос {currentIdxSafe + 1}/{answers.length}
              </span>
              <Badge
                className={
                  (currentAnswer.points_earned || 0) > 0
                    ? 'bg-green-100 text-green-800 hover:bg-green-100'
                    : 'bg-gray-100 text-gray-800 hover:bg-gray-100'
                }
                variant="secondary"
              >
                {pointsBadgeText}
              </Badge>
            </div>

            <TypstRender source={currentAnswer.question_text || ''} mode="review" />

            {mediaFiles.length > 0 && (
              <MediaCarousel files={mediaFiles} mode="review" />
            )}

            <AnswerBlocks
              question={currentQuestion}
              mode="review"
              value={reviewAnswerFor(currentQuestion.id)}
              correctOptionIds={reviewCorrectIdsFor(currentQuestion.id)}
              explanation={explanationFor(currentQuestion.id)}
            />

            {(currentAnswer.question_type === 'TEXT' ||
              currentAnswer.question_type === 'ESSAY') &&
              currentAnswer.is_correct === null && (
                <div className="rounded-lg border p-3 bg-gray-50 text-gray-700 text-sm">
                  <AlertCircle className="h-4 w-4 inline mr-2" />
                  Требует проверки вручную
                </div>
              )}

            <div className="flex justify-between pt-4">
              <Button
                variant="outline"
                disabled={currentIdxSafe === 0}
                onClick={() =>
                  setCurrentIndex((i) => Math.max(0, i - 1))
                }
              >
                Предыдущий
              </Button>
              <Button
                disabled={currentIdxSafe === answers.length - 1}
                onClick={() =>
                  setCurrentIndex((i) =>
                    Math.min(answers.length - 1, i + 1)
                  )
                }
              >
                Следующий
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
