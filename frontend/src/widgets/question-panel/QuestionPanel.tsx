/**
 * QuestionPanel — 240px scrollable side panel with question list.
 *
 * Row styles adapt to mode: current, answered, correct, wrong, unanswered.
 */
import { Check, Circle, Plus, X } from 'lucide-react'
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

  const rowClass = (index: number) => {
    let base = 'flex items-center justify-between px-3 py-2 rounded-md text-sm cursor-pointer transition-colors'
    const q = questions[index]
    const isCurrent = index === currentIndex
    const qid = String(q.id)

    if (isCurrent) {
      base += ' bg-primary/10 border-l-4 border-primary'
    }

    if (isReview && results) {
      const r = results[qid]
      if (r) {
        if (r.isCorrect) base += ' bg-green-50 text-green-700'
        else base += ' bg-red-50 text-red-700'
      } else {
        base += ' text-muted-foreground'
      }
    } else if (isCurrent) {
      base += ' text-foreground'
    } else if (answers && answers[qid] !== undefined && answers[qid] !== null && answers[qid] !== '') {
      base += ' text-green-600'
    } else {
      base += ' text-muted-foreground'
    }

    if (!isCurrent) base += ' hover:bg-accent'
    return base
  }

  const iconFor = (index: number) => {
    const q = questions[index]
    const qid = String(q.id)

    if (isReview && results) {
      const r = results[qid]
      if (r && r.isCorrect) return <Check className="h-4 w-4 text-green-600" />
      if (r && !r.isCorrect) return <X className="h-4 w-4 text-red-600" />
      return <Circle className="h-4 w-4 text-muted-foreground" />
    }

    if (answers && answers[qid] !== undefined && answers[qid] !== null && answers[qid] !== '') {
      return <Check className="h-4 w-4 text-green-600" />
    }

    return <Circle className="h-4 w-4 text-muted-foreground" />
  }

  const pointsFor = (index: number) => {
    if (!isReview || !results) return null
    const r = results[String(questions[index].id)]
    if (!r) return null
    return (
      <span className="text-xs ml-2">
        {r.pointsEarned}/{r.maxPoints} {r.maxPoints === 1 ? 'pt' : 'pts'}
      </span>
    )
  }

  return (
    <div className="w-60 h-full flex flex-col border-r bg-background">
      <div className="p-3 font-semibold text-sm border-b">Questions</div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {questions.map((q, i) => (
          <div key={q.id} className={rowClass(i)} onClick={() => onSelect(i)}>
            <div className="flex items-center gap-2 truncate">
              {iconFor(i)}
              <span className="truncate">
                {i + 1}. {q.text ? q.text.substring(0, 30) + (q.text.length > 30 ? '...' : '') : '(empty)'}
              </span>
            </div>
            <div className="flex items-center gap-1 shrink-0">
              {pointsFor(i)}
              {isEdit && onDeleteQuestion && (
                <button
                  className="ml-1 rounded-sm hover:bg-destructive/20 p-0.5"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDeleteQuestion(i)
                  }}
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
      {isEdit && (onAddQuestion || onAddFromPool) && (
        <div className="p-2 border-t space-y-2">
          {onAddQuestion && (
            <Button variant="outline" size="sm" className="w-full" onClick={onAddQuestion}>
              <Plus className="h-4 w-4 mr-1" />
              Add Question
            </Button>
          )}
          {onAddFromPool && (
            <Button variant="secondary" size="sm" className="w-full" onClick={onAddFromPool}>
              <Plus className="h-4 w-4 mr-1" />
              From Pool
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
