/**
 * TakeTestPage — unified take / edit / review template.
 *
 * Layout: fixed 240px side panel + scrollable main area.
 */
import { useState, useEffect } from 'react'
import { useParams, useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft, Clock, CheckCircle2, XCircle, BarChart3 } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Loader } from '@/shared/ui/loader'
import { Card, CardContent } from '@/shared/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/shared/ui/dialog'
import { useToast } from '@/shared/hooks/useToast'
import { useAuth } from '@/shared/hooks/useAuth'
import { formatTime } from '@/shared/lib/utils'
import { formatDuration } from '@/shared/lib/format'
import {
  getTestApiV1TestsTestIdGet,
  startAttemptApiV1AttemptsPost,
  getAttemptApiV1AttemptsAttemptIdGet,
  getActiveAttemptApiV1AttemptsActiveGet,
  submitAnswerApiV1AttemptsAttemptIdAnswersPost,
  finishAttemptApiV1AttemptsAttemptIdFinishPost,
  getResultApiV1AttemptsAttemptIdResultGet,
  addQuestionApiV1TestsTestIdQuestionsPost,
  updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch,
  deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete,
  updateTestApiV1TestsTestIdPatch,
  deleteTestApiV1TestsTestIdDelete,
} from '@/shared/api'
import type {
  QuestionResponse,
  QuestionAuthorResponse,
  AttemptResultResponse,
  AttemptResponse,
  TestAuthorDetailResponse,
  TestDetailResponse,
  OptionAuthorResponse,
} from '@/shared/api'

import QuestionPanel from '@/widgets/question-panel/QuestionPanel'
import QuestionPoolModal from '@/widgets/question-pool-modal/QuestionPoolModal'
import TypstRender from '@/shared/components/TypstRender'
import MediaCarousel from '@/shared/components/MediaCarousel'
import AnswerBlocks from '@/shared/components/AnswerBlocks'

export default function TakeTestPage({ editMode = false }: { editMode?: boolean }) {
  const { testId, attemptId } = useParams()
  const location = useLocation()
  const navigate = useNavigate()
  const toast = useToast()
  const { isAuthed, requireAuth } = useAuth()

  const mode: 'take' | 'edit' | 'review' = editMode
    ? 'edit'
    : location.pathname.startsWith('/attempts/')
      ? 'review'
      : 'take'

  const numTestId = testId ? Number(testId) : 0
  const numAttemptId = attemptId ? Number(attemptId) : 0

  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [title, setTitle] = useState('')
  const [timerSeconds, setTimerSeconds] = useState(0)

  const [questions, setQuestions] = useState<(QuestionResponse | QuestionAuthorResponse)[]>([])

  const [activeAttemptId, setActiveAttemptId] = useState<number | null>(null)
  const [answers, setAnswers] = useState<Record<number, unknown>>({})

  const [reviewAttempt, setReviewAttempt] = useState<AttemptResultResponse | null>(null)

  const [summaryResult, setSummaryResult] = useState<AttemptResultResponse | null>(null)
  const [showSummary, setShowSummary] = useState(false)
  const [poolModalOpen, setPoolModalOpen] = useState(false)

  const [pendingPatch, setPendingPatch] = useState<Partial<QuestionAuthorResponse> | null>(null)
  const [isDraft, setIsDraft] = useState(false)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)

  // load test (take / edit)
  useEffect(() => {
    if (mode === 'review' || !numTestId) return
    let cancelled = false
    async function load() {
      try {
        const res = await getTestApiV1TestsTestIdGet({ path: { test_id: numTestId } })
        const data = res.data as TestAuthorDetailResponse | TestDetailResponse | undefined
        if (!cancelled && data) {
          setTitle(data.title || '')
          if (data.questions) setQuestions(data.questions)
          if (mode === 'edit') {
            setIsDraft((data as TestAuthorDetailResponse).is_public === false)
          }
        }
      } catch {
        // ignore
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [mode, numTestId])

  // load review data
  useEffect(() => {
    if (mode !== 'review' || !numAttemptId) return
    let cancelled = false
    async function load() {
      try {
        const res = await getResultApiV1AttemptsAttemptIdResultGet({ path: { attempt_id: numAttemptId } })
        const data = res.data as AttemptResultResponse | undefined
        if (!cancelled && data) {
          setReviewAttempt(data)
          setTitle(data.test_title || '')
          // fetch real questions for option texts
          try {
            const tRes = await getTestApiV1TestsTestIdGet({ path: { test_id: data.test_id } })
            const tData = tRes.data as TestAuthorDetailResponse | TestDetailResponse | undefined
            if (!cancelled && tData?.questions) {
              setQuestions(tData.questions)
            } else {
              setQuestions(
                data.answers?.map((a) => ({
                  id: a.question_id,
                  question_type: a.question_type,
                  text: a.question_text,
                  order_number: 0,
                  points: a.points,
                  explanation: a.explanation,
                  correct_answer: null,
                  image_url: null,
                  options:
                    a.correct_option_ids?.map((cid, i) => ({
                      id: cid,
                      text: `Option ${i + 1}`,
                      order_number: i + 1,
                      is_correct: true,
                    })) || [],
                })) || []
              )
            }
          } catch {}
        }
      } catch (e) {
        // ignore
      } finally {
        if (!cancelled) setIsLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [mode, numAttemptId])

  // take mode: init attempt
  useEffect(() => {
    if (mode !== 'take' || !numTestId) return
    if (!isAuthed) {
      requireAuth(location.pathname)
      return
    }
    let cancelled = false
    async function init() {
      const cacheKey = `wep_attempt_${numTestId}`
      const raw = localStorage.getItem(cacheKey)
      let cache: { attemptId?: number; currentIndex?: number; answers?: Record<string, unknown> } | null = null
      if (raw) {
        try { cache = JSON.parse(raw) } catch {}
      }
      if (cache?.attemptId) {
        try {
          const res = await getAttemptApiV1AttemptsAttemptIdGet({ path: { attempt_id: cache.attemptId } })
          const data = res.data as AttemptResponse | undefined
          if (data && data.status === 'in_progress') {
            if (!cancelled) {
              setActiveAttemptId(data.id)
              setTimerSeconds(Math.floor((Date.now() - new Date(data.started_at).getTime()) / 1000))
              if (cache?.answers) {
                const mapped: Record<number, unknown> = {}
                Object.entries(cache.answers).forEach(([k, v]) => {
                  mapped[Number(k)] = (v as { value?: unknown })?.value ?? v
                })
                setAnswers(mapped)
              }
              if (cache?.currentIndex !== undefined) setCurrentIndex(cache.currentIndex)
            }
            return
          }
        } catch {}
      }
      try {
        const activeRes = await getActiveAttemptApiV1AttemptsActiveGet({ query: { test_id: numTestId } })
        const activeData = activeRes.data as { has_active?: boolean; attempt_id?: number } | undefined
        if (activeData?.has_active && activeData.attempt_id) {
          const res = await getAttemptApiV1AttemptsAttemptIdGet({ path: { attempt_id: activeData.attempt_id } })
          const data = res.data as AttemptResponse | undefined
          if (!cancelled && data && data.status === 'in_progress') {
            setActiveAttemptId(data.id)
            setTimerSeconds(Math.floor((Date.now() - new Date(data.started_at).getTime()) / 1000))
            localStorage.setItem(
              cacheKey,
              JSON.stringify({
                attemptId: data.id,
                testId: numTestId,
                currentIndex: 0,
                answers: {},
                startedAt: data.started_at,
              })
            )
            return
          }
        }
      } catch {}
      try {
        const res = await startAttemptApiV1AttemptsPost({ body: { test_id: numTestId } })
        const data = res.data as AttemptResponse | undefined
        if (!cancelled && data) {
          setActiveAttemptId(data.id)
          setTimerSeconds(0)
          localStorage.setItem(
            cacheKey,
            JSON.stringify({
              attemptId: data.id,
              testId: numTestId,
              currentIndex: 0,
              answers: {},
              startedAt: data.started_at,
            })
          )
        }
      } catch {
        toast.error('Failed to start attempt')
      }
    }
    init()
    return () => { cancelled = true }
  }, [mode, numTestId, isAuthed, requireAuth, toast, location.pathname])

  // timer
  useEffect(() => {
    if (mode !== 'take' || !activeAttemptId) return
    const interval = setInterval(() => setTimerSeconds((s) => s + 1), 1000)
    return () => clearInterval(interval)
  }, [mode, activeAttemptId])

  // edit auto-save
  useEffect(() => {
    if (mode !== 'edit' || !numTestId || !pendingPatch) return
    const timer = setTimeout(async () => {
      const q = questions[currentIndex] as QuestionAuthorResponse | undefined
      if (!q) return
      const body: any = { ...pendingPatch }
      if (body.options) {
        body.options = body.options.map((o: OptionAuthorResponse) => ({
          text: o.text,
          is_correct: o.is_correct,
          order_number: o.order_number,
        }))
      }
      try {
        await updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch({
          path: { test_id: numTestId, question_id: q.id },
          body,
        })
      } catch {
        toast.error('Auto-save failed')
      }
      setPendingPatch(null)
    }, 2000)
    return () => clearTimeout(timer)
  }, [mode, numTestId, pendingPatch, questions, currentIndex, toast])

  const handleAnswerChange = async (value: unknown) => {
    if (mode !== 'take') return
    const q = questions[currentIndex] as QuestionResponse | undefined
    if (!q || !activeAttemptId) return
    setAnswers((prev) => ({ ...prev, [q.id]: value }))

    const payload: {
      question_id: number
      selected_option_ids?: number[] | null
      text_answer?: string | null
      matching_answer?: Record<string, number> | null
      file_answer?: string | null
    } = {
      question_id: q.id,
    }
    const qt = q.question_type as string
    if (qt === 'SINGLE_CHOICE') {
      payload.selected_option_ids = value != null ? [value as number] : null
    } else if (qt === 'MULTIPLE_CHOICE') {
      payload.selected_option_ids = (value as number[]) || null
    } else if (qt === 'TEXT' || qt === 'ESSAY') {
      payload.text_answer = (value as string) || null
    } else if (qt === 'MATCHING') {
      payload.matching_answer = (value as Record<string, number>) || null
    } else if (qt === 'FILE_UPLOAD') {
      payload.file_answer = (value as string) || null
    }

    const cacheKey = `wep_attempt_${numTestId}`
    const raw = localStorage.getItem(cacheKey)
    let cacheObj: any = { attemptId: activeAttemptId, testId: numTestId, currentIndex, answers: {} }
    if (raw) {
      try { cacheObj = JSON.parse(raw) } catch {}
    }
    cacheObj.answers[q.id] = {
      questionId: String(q.id),
      type: q.question_type,
      value,
      answeredAt: new Date().toISOString(),
    }
    cacheObj.currentIndex = currentIndex
    localStorage.setItem(cacheKey, JSON.stringify(cacheObj))

    try {
      await submitAnswerApiV1AttemptsAttemptIdAnswersPost({
        path: { attempt_id: activeAttemptId },
        body: payload,
      })
    } catch {
      // ignore network errors, cached locally
    }
  }

  const handleFinish = async () => {
    if (mode !== 'take' || !activeAttemptId) return
    try {
      await finishAttemptApiV1AttemptsAttemptIdFinishPost({ path: { attempt_id: activeAttemptId } })
      localStorage.removeItem(`wep_attempt_${numTestId}`)
      const res = await getResultApiV1AttemptsAttemptIdResultGet({ path: { attempt_id: activeAttemptId } })
      const data = res.data as AttemptResultResponse | undefined
      if (data) {
        setSummaryResult(data)
        setShowSummary(true)
      } else {
        navigate(`/attempts/${activeAttemptId}`)
      }
    } catch {
      toast.error('Failed to finish attempt')
    }
  }

  const handleAddQuestion = async () => {
    if (mode !== 'edit' || !numTestId) return
    try {
      const res = await addQuestionApiV1TestsTestIdQuestionsPost({
        path: { test_id: numTestId },
        body: {
          question_type: 'SINGLE_CHOICE',
          text: '',
          order_number: questions.length + 1,
          points: 1,
          options: [{ text: 'Option 1', is_correct: false, order_number: 1 }],
        },
      })
      const data = res.data as QuestionAuthorResponse | undefined
      if (data) {
        setQuestions((prev) => [...prev, data])
        setCurrentIndex(questions.length)
      }
    } catch {
      toast.error('Failed to add question')
    }
  }

  const handleDeleteQuestion = async (index: number) => {
    if (mode !== 'edit' || !numTestId) return
    const q = questions[index] as QuestionAuthorResponse | undefined
    if (!q) return
    if (!window.confirm('Delete this question?')) return
    try {
      await deleteQuestionApiV1TestsTestIdQuestionsQuestionIdDelete({
        path: { test_id: numTestId, question_id: q.id },
      })
      setQuestions((prev) => prev.filter((_, i) => i !== index))
      if (currentIndex >= index && currentIndex > 0) {
        setCurrentIndex((i) => i - 1)
      }
    } catch {
      toast.error('Failed to delete question')
    }
  }

  const handlePublish = async () => {
    if (mode !== 'edit' || !numTestId) return
    try {
      await updateTestApiV1TestsTestIdPatch({
        path: { test_id: numTestId },
        body: { is_public: true },
      })
      setIsDraft(false)
      toast.success('Тест опубликован')
    } catch {
      toast.error('Не удалось опубликовать тест')
    }
  }

  const handleDeleteTest = async () => {
    if (mode !== 'edit' || !numTestId) return
    try {
      await deleteTestApiV1TestsTestIdDelete({
        path: { test_id: numTestId },
      })
      toast.success('Тест удалён')
      navigate('/my-tests')
    } catch {
      toast.error('Не удалось удалить тест')
    }
  }

  const handleAddFromPool = (data?: QuestionAuthorResponse) => {
    if (data) {
      setQuestions((prev) => [...prev, data])
      setCurrentIndex(questions.length)
      setPoolModalOpen(false)
    }
  }

  const handleQuestionChange = (patch: Partial<QuestionAuthorResponse>) => {
    if (mode !== 'edit') return
    setQuestions((prev) => {
      const next = [...prev]
      next[currentIndex] = { ...next[currentIndex], ...patch } as QuestionAuthorResponse
      return next
    })
    setPendingPatch((prev) => ({ ...prev, ...patch }))
  }

  const currentQuestion = questions[currentIndex]

  const mediaFiles = (currentQuestion?.media_files ?? []).map((url, i) => ({
    id: `media-${i}`,
    url,
    type: 'image' as const,
    filename: `media-${i}`,
  }))

  const reviewResults = (() => {
    if (mode !== 'review' || !reviewAttempt?.answers) return undefined
    const map: Record<string, { isCorrect: boolean; pointsEarned: number; maxPoints: number }> = {}
    reviewAttempt.answers.forEach((a) => {
      map[a.question_id] = {
        isCorrect: a.is_correct ?? false,
        pointsEarned: a.points_earned ?? 0,
        maxPoints: a.points,
      }
    })
    return map
  })()

  const reviewAnswerFor = (qid: number): unknown | undefined => {
    if (mode !== 'review') return undefined
    const ans = reviewAttempt?.answers?.find((a) => a.question_id === qid)
    if (!ans) return undefined
    if (ans.question_type === 'SINGLE_CHOICE') return ans.selected_option_ids?.[0] ?? null
    if (ans.question_type === 'MULTIPLE_CHOICE') return ans.selected_option_ids ?? []
    if (ans.question_type === 'MATCHING') return ans.matching_answer ?? {}
    if (ans.question_type === 'FILE_UPLOAD') return ans.file_answer ?? ''
    return ans.text_answer ?? ''
  }

  const reviewCorrectIdsFor = (qid: number): number[] => {
    if (mode !== 'review') return []
    return reviewAttempt?.answers?.find((a) => a.question_id === qid)?.correct_option_ids ?? []
  }

  const explanationFor = (qid: number): string | null => {
    if (mode !== 'review') return null
    return reviewAttempt?.answers?.find((a) => a.question_id === qid)?.explanation ?? null
  }

  const scoreText = (() => {
    if (mode === 'review' && reviewAttempt) {
      return `${reviewAttempt.score}/${reviewAttempt.max_score}`
    }
    return ''
  })()

  const backTo =
    mode === 'edit' ? '/my-tests' : mode === 'review' ? '/history' : `/tests/${numTestId}`

  if (isLoading && !questions.length) {
    return (
      <div className="h-screen flex items-center justify-center">
        <Loader />
      </div>
    )
  }

  if (!questions.length && mode !== 'edit') {
    return (
      <div className="h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">No questions found.</p>
        <Button variant="outline" onClick={() => navigate(backTo)}>
          Back
        </Button>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      {/* Top bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b h-14 shrink-0">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate(backTo)}>
            <ArrowLeft className="h-4 w-4 mr-1" />
            Back
          </Button>
          <h1 className="text-sm font-semibold truncate max-w-[40vw]">{title}</h1>
        </div>
        <div className="flex items-center gap-3">
          {mode === 'take' && (
            <>
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Clock className="h-4 w-4" />
                {formatTime(timerSeconds)}
              </div>
              <span className="text-sm text-muted-foreground">
                {currentIndex + 1}/{questions.length}
              </span>
              <Button size="sm" onClick={handleFinish}>
                Finish
              </Button>
            </>
          )}
          {mode === 'edit' && (
            <>
              {isDraft && (
                <Button variant="default" size="sm" onClick={handlePublish}>
                  Опубликовать
                </Button>
              )}
              {isDraft && (
                <Button variant="destructive" size="sm" onClick={() => setDeleteConfirmOpen(true)}>
                  Удалить
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={() => navigate(`/tests/${testId}/settings`)}>
                Settings
              </Button>
            </>
          )}
          {mode === 'review' && (
            <span className="text-sm font-medium">Score: {scoreText}</span>
          )}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 flex overflow-hidden">
        {questions.length > 0 && (
          <QuestionPanel
            questions={questions}
            currentIndex={currentIndex}
            onSelect={setCurrentIndex}
            mode={mode}
            answers={mode === 'take' ? answers : undefined}
            results={reviewResults}
            onAddQuestion={mode === 'edit' ? handleAddQuestion : undefined}
            onDeleteQuestion={mode === 'edit' ? handleDeleteQuestion : undefined}
            onAddFromPool={mode === 'edit' ? () => setPoolModalOpen(true) : undefined}
          />
        )}
        <div className="flex-1 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 md:p-6">
            {showSummary && summaryResult ? (
              <div className="max-w-lg mx-auto space-y-6 py-12">
                <div className="text-center space-y-3">
                  <div className="text-5xl font-bold">
                    {summaryResult.score}
                    <span className="text-2xl text-muted-foreground font-nomal">/{summaryResult.max_score}</span>
                  </div>
                  <p className="text-lg text-muted-foreground">Test completed!</p>
                </div>

                <div className="flex justify-center gap-6">
                  <div className="text-center">
                    <div className="flex items-center gap-1.5 text-green-600">
                      <CheckCircle2 className="h-5 w-5" />
                      <span className="text-xl font-semibold">
                        {summaryResult.answers?.filter((a) => a.is_correct === true).length ?? 0}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">Correct</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center gap-1.5 text-red-600">
                      <XCircle className="h-5 w-5" />
                      <span className="text-xl font-semibold">
                        {summaryResult.answers?.filter((a) => a.is_correct === false).length ?? 0}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">Wrong</p>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center gap-1.5 text-muted-foreground">
                      <BarChart3 className="h-5 w-5" />
                      <span className="text-xl font-semibold">
                        {(() => {
                          const s = summaryResult.started_at ? new Date(summaryResult.started_at).getTime() : 0
                          const f = summaryResult.finished_at ? new Date(summaryResult.finished_at).getTime() : Date.now()
                          return formatDuration(Math.max(0, Math.floor((f - s) / 1000)))
                        })()}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">Time</p>
                  </div>
                </div>

                {summaryResult.answers && (
                  <Card>
                    <CardContent className="pt-6">
                      <div className="space-y-2">
                        {summaryResult.answers.map((a, i) => (
                          <div key={a.question_id} className="flex items-center justify-between text-sm">
                            <span className="truncate flex-1">Q{i + 1}</span>
                            <span className={a.is_correct === true ? 'text-green-600 font-medium' : a.is_correct === false ? 'text-red-600 font-medium' : 'text-muted-foreground'}>
                              {a.points_earned ?? 0}/{a.points}
                            </span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                <div className="flex justify-center gap-3 pt-4">
                  <Button onClick={() => navigate(`/attempts/${summaryResult.attempt_id}`)}>
                    View details
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/catalog')}>
                    Back to catalog
                  </Button>
                </div>
              </div>
            ) : currentQuestion ? (
              <div className="max-w-3xl mx-auto space-y-6">
                <TypstRender
                  source={currentQuestion.text || ''}
                  testId={numTestId}
                  questionId={currentQuestion.id}
                  mode={mode}
                />
                {(mode === 'edit' || mediaFiles.length > 0) && (
                  <MediaCarousel
                    files={mediaFiles}
                    mode={mode}
                    onChange={
                      mode === 'edit'
                        ? (next: { url: string }[]) =>
                            handleQuestionChange({
                              media_files: next.map((f) => f.url),
                            })
                        : undefined
                    }
                  />
                )}
                <AnswerBlocks
                  question={currentQuestion}
                  mode={mode}
                  value={
                    mode === 'review'
                      ? reviewAnswerFor(currentQuestion.id)
                      : answers[currentQuestion.id]
                  }
                  onChange={handleAnswerChange}
                  onQuestionChange={mode === 'edit' ? handleQuestionChange : undefined}
                  correctOptionIds={reviewCorrectIdsFor(currentQuestion.id)}
                  explanation={explanationFor(currentQuestion.id)}
                />
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full gap-4">
                <p className="text-muted-foreground">Select a question to begin.</p>
                {mode === 'edit' && (
                  <Button onClick={handleAddQuestion}>Add Question</Button>
                )}
              </div>
            )}
          </div>

          {/* Fixed bottom navigation */}
          {showSummary ? null : currentQuestion && !showSummary && (
            <div className="flex justify-between px-4 md:px-6 py-3 border-t bg-background shrink-0">
              <Button
                variant="outline"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              >
                Previous
              </Button>
              {currentIndex < questions.length - 1 ? (
                <Button
                  onClick={() =>
                    setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))
                  }
                >
                  Next
                </Button>
              ) : mode === 'take' ? (
                <Button onClick={handleFinish}>Submit All</Button>
              ) : null}
            </div>
          )}
        </div>
      </div>
      {mode === 'edit' && (
        <QuestionPoolModal
          testId={numTestId}
          open={poolModalOpen}
          onClose={() => setPoolModalOpen(false)}
          onAdded={handleAddFromPool}
        />
      )}
      {mode === 'edit' && (
        <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Удалить черновик?</DialogTitle>
              <DialogDescription>
                Это действие нельзя отменить. Черновик будет удален навсегда.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
                Отмена
              </Button>
              <Button variant="destructive" onClick={handleDeleteTest}>
                Удалить
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}
