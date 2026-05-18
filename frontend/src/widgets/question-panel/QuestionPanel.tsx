import { Check, Circle, Plus, X, BookOpen } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import type { QuestionResponse, QuestionAuthorResponse } from '@/shared/api'

type AnyQuestion = QuestionResponse | QuestionAuthorResponse

interface QuestionPanelProps {
  questions: AnyQuestion[]
  currentIndex: number
  onSelect: (index: number) => void
  mode: 'take' | 'edit' | 'review'
  answers?: Record<string, unknown>
  results?: Record<string, { isCorrect: boolean; pointsEarned: number; maxPoints: number }>
  onAddQuestion?: () => void
  onDeleteQuestion?: (index: number) => void
  onAddFromPool?: () => void
}

export default function QuestionPanel({
  questions,
  currentIndex,
  onSelect,
  mode,
  answers,
  results,
  onAddQuestion,
  onDeleteQuestion,
  onAddFromPool,
}: QuestionPanelProps) {
  const isEdit = mode === 'edit'
  const isReview = mode === 'review'

  const rowState = (index: number) => {
    const q = questions[index]
    const qid = String(q.id)
    const isCurrent = index === currentIndex

    if (isReview && results) {
      const r = results[qid]
      if (r?.isCorrect) return 'correct'
      if (r && !r.isCorrect) return 'wrong'
      return 'neutral'
    }
    if (isCurrent) return 'current'
    if (answers?.[qid] !== undefined && answers[qid] !== null && answers[qid] !== '') return 'answered'
    return 'idle'
  }

  const rowCls = (index: number) => {
    const state = rowState(index)
    const base = 'group relative flex items-center gap-2 px-3 py-2 rounded-lg text-sm cursor-pointer transition-all'
    const isCurrent = index === currentIndex
    switch (state) {
      case 'current':  return `${base} bg-primary/10 text-primary font-medium ring-1 ring-primary/30`
      case 'answered': return `${base} ${isCurrent ? 'bg-primary/10 text-primary font-medium ring-1 ring-primary/30' : 'text-foreground hover:bg-accent'}`
      case 'correct':  return `${base} bg-green-50 text-green-800 ${isCurrent ? 'ring-1 ring-green-400' : 'hover:bg-green-100'}`
      case 'wrong':    return `${base} bg-red-50 text-red-800 ${isCurrent ? 'ring-1 ring-red-400' : 'hover:bg-red-100'}`
      default:         return `${base} text-muted-foreground hover:bg-accent`
    }
  }

  const iconFor = (index: number) => {
    const state = rowState(index)
    const isCurrent = index === currentIndex
    if (state === 'correct') return <Check className="h-3.5 w-3.5 text-green-600 shrink-0" />
    if (state === 'wrong')   return <X     className="h-3.5 w-3.5 text-red-500 shrink-0" />
    if (state === 'answered' || isCurrent)
      return <div className="h-3.5 w-3.5 rounded-full bg-primary shrink-0" />
    return <Circle className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
  }

  const pointsFor = (index: number) => {
    if (!isReview || !results) return null
    const r = results[String(questions[index].id)]
    if (!r) return null
    return (
      <span className="ml-auto text-xs font-medium shrink-0">
        {r.pointsEarned}/{r.maxPoints}
      </span>
    )
  }

  const previewText = (q: AnyQuestion, i: number) => {
    const raw = q.text || ''
    const stripped = raw.replace(/[#$`]/g, '').trim()
    const short = stripped.substring(0, 28)
    return `${i + 1}. ${short}${stripped.length > 28 ? '…' : ''}`
  }

  return (
    <div className="w-60 h-full flex flex-col border-r bg-background/95 backdrop-blur-sm">
      <div className="flex items-center gap-2 px-4 py-3 border-b">
        <BookOpen className="h-4 w-4 text-muted-foreground" />
        <span className="text-sm font-semibold">Вопросы</span>
        <span className="ml-auto text-xs text-muted-foreground bg-muted rounded-full px-2 py-0.5">
          {questions.length}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-2 space-y-0.5">
        {questions.map((q, i) => (
          <div
            key={q.id}
            className={rowCls(i)}
            onClick={() => onSelect(i)}
          >
            {iconFor(i)}
            <span className="flex-1 truncate leading-snug">{previewText(q, i)}</span>
            {pointsFor(i)}
            {isEdit && onDeleteQuestion && (
              <button
                className="opacity-0 group-hover:opacity-100 shrink-0 rounded hover:bg-destructive/20 p-0.5 transition-opacity"
                onClick={(e) => { e.stopPropagation(); onDeleteQuestion(i) }}
              >
                <X className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
              </button>
            )}
          </div>
        ))}

        {isEdit && questions.length === 0 && (
          <div className="py-8 text-center text-xs text-muted-foreground">
            Нет вопросов.<br />Добавьте первый.
          </div>
        )}
      </div>

      {isEdit && (onAddQuestion || onAddFromPool) && (
        <div className="p-2 border-t space-y-1.5">
          {onAddQuestion && (
            <Button variant="default" size="sm" className="w-full" onClick={onAddQuestion}>
              <Plus className="h-4 w-4 mr-1.5" />
              Добавить вопрос
            </Button>
          )}
          {onAddFromPool && (
            <Button variant="outline" size="sm" className="w-full text-xs" onClick={onAddFromPool}>
              <Plus className="h-3.5 w-3.5 mr-1.5" />
              Из банка вопросов
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
