import {useState, useEffect, useRef} from 'react'
import {useParams, useNavigate, useSearchParams} from 'react-router-dom'
import {useTestDetail} from '@/features/test-management/api/useTests'
import {useStartAttempt, useSubmitAnswer, useFinishAttempt} from '@/features/taking/api/useTaking'
import {useAttemptStore} from '@/entities/attempt/model/store'
import {Button} from '@/shared/ui/button'
import {Card, CardContent} from '@/shared/ui/card'
import {Checkbox} from '@/shared/ui/checkbox'
import {RadioGroup, RadioGroupItem} from '@/shared/ui/radio-group'
import {Label} from '@/shared/ui/label'
import {Input} from '@/shared/ui/input'
import {Loader} from '@/shared/ui/loader'

export default function TakeTestPage() {
  const {testId} = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const attemptIdParam = searchParams.get('attemptId')

  const {data: test, isLoading} = useTestDetail(Number(testId))
  const start = useStartAttempt()
  const submit = useSubmitAnswer(Number(attemptIdParam) || 0)
  const finish = useFinishAttempt(Number(attemptIdParam) || 0)
  const attemptStore = useAttemptStore()

  const questions = (test?.data as any)?.questions || []
  const [activeIdx, setActiveIdx] = useState(0)
  const activeQuestion = questions[activeIdx]

  const [remaining, setRemaining] = useState<number | null>(null)
  const expiredRef = useRef(false)
  const finishRef = useRef(finish)
  finishRef.current = finish

  const expiresAt = (attemptStore.currentAttempt as any)?.expires_at

  useEffect(() => {
    if (attemptIdParam) {
      const id = Number(attemptIdParam)
      const state = useAttemptStore.getState()
      if (!state.currentAttempt || state.currentAttempt.id !== id) {
        state.setCurrentAttempt({id} as any)
      }
    }
  }, [attemptIdParam])

  useEffect(() => {
    if (!expiresAt) {
      setRemaining(null)
      return
    }
    const end = new Date(expiresAt).getTime()
    const tick = () => {
      const seconds = Math.max(0, Math.ceil((end - Date.now()) / 1000))
      setRemaining(seconds)
      if (seconds <= 0 && !expiredRef.current) {
        expiredRef.current = true
        finishRef.current.mutate(undefined, {
          onSuccess: () => navigate(`/results/${attemptIdParam}`),
        })
      }
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [expiresAt, navigate, attemptIdParam])

  if (isLoading) return <Loader />

  if (!attemptIdParam) {
    return (
      <div className="max-w-3xl mx-auto p-6 space-y-4 text-center">
        <h1 className="text-2xl font-bold">{(test?.data as any)?.title}</h1>
        <p className="text-muted-foreground">{(test?.data as any)?.description}</p>
        <p className="text-sm text-muted-foreground">Вопросов: {questions.length}</p>
        <Button onClick={() => start.mutate(Number(testId), {onSuccess: (res: any) => {
          const data = res.data || res
          attemptStore.setCurrentAttempt(data)
          navigate(`/take/${testId}?attemptId=${data.id}`)
        }})}>Начать тест</Button>
      </div>
    )
  }

  const handleAnswer = (payload: any) => {
    attemptStore.setAnswer(activeQuestion.id, payload)
    submit.mutate({question_id: activeQuestion.id, ...payload})
  }

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">{(test?.data as any)?.title}</h1>
        <div className="flex items-center gap-4">
          {remaining !== null && (
            <span className="text-sm font-mono text-red-600">
              {String(Math.floor(remaining / 60)).padStart(2, '0')}:
              {String(remaining % 60).padStart(2, '0')}
            </span>
          )}
          <span className="text-sm text-muted-foreground">{activeIdx + 1} / {questions.length}</span>
        </div>
      </div>
      <div className="flex gap-2 overflow-x-auto pb-2">
        {questions.map((_: any, idx: number) => (
          <button key={idx} className={`px-3 py-1 rounded border text-sm ${idx === activeIdx ? 'bg-black text-white' : ''}`} onClick={() => setActiveIdx(idx)}>{idx + 1}</button>
        ))}
      </div>
      {activeQuestion && (
        <Card>
          <CardContent className="p-4 space-y-4">
            <p className="font-medium">{activeQuestion.text}</p>
            {activeQuestion.image_url && <img src={activeQuestion.image_url} alt="media" className="max-w-md rounded" />}
            {activeQuestion.question_type === 'single_choice' && (
              <RadioGroup onValueChange={(v) => handleAnswer({selected_option_ids: [Number(v)]})}>
                {activeQuestion.options.map((o: any) => (
                  <div key={o.id} className="flex items-center gap-2">
                    <RadioGroupItem value={String(o.id)} id={`opt-${o.id}`} />
                    <Label htmlFor={`opt-${o.id}`}>{o.text}</Label>
                  </div>
                ))}
              </RadioGroup>
            )}
            {activeQuestion.question_type === 'multiple_choice' && (
              <div className="space-y-2">
                {activeQuestion.options.map((o: any) => (
                  <div key={o.id} className="flex items-center gap-2">
                    <Checkbox onCheckedChange={(checked) => {
                      const current = attemptStore.answers[activeQuestion.id]?.selectedOptionIds || []
                      const next = checked ? [...current, o.id] : current.filter((id: number) => id !== o.id)
                      handleAnswer({selected_option_ids: next})
                    }} />
                    <Label>{o.text}</Label>
                  </div>
                ))}
              </div>
            )}
            {activeQuestion.question_type === 'text_input' && (
              <Input placeholder="Ваш ответ" onBlur={(e) => handleAnswer({text_answer: e.target.value})} />
            )}
            <div className="flex justify-between pt-2">
              <Button variant="outline" disabled={activeIdx === 0} onClick={() => setActiveIdx(i => i - 1)}>Назад</Button>
              {activeIdx < questions.length - 1 ? (
                <Button onClick={() => setActiveIdx(i => i + 1)}>Далее</Button>
              ) : (
                <Button onClick={() => finish.mutate(undefined, {onSuccess: () => navigate(`/results/${attemptIdParam}`)})}>Завершить</Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
