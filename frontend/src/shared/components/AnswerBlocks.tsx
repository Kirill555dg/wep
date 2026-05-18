/**
 * AnswerBlocks — renders interactive or read-only answer widgets.
 *
 * Handles SINGLE_CHOICE, MULTIPLE_CHOICE, TEXT, ESSAY.
 * Edit mode exposes inline inputs for type, points, options, explanation.
 */
import { Check, Plus, X } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Checkbox } from '@/shared/ui/checkbox'
import { Select, SelectItem } from '@/shared/ui/select'
import type { QuestionType, QuestionResponse, QuestionAuthorResponse, OptionAuthorResponse } from '@/shared/api'

type AnyQuestion = QuestionResponse | QuestionAuthorResponse

function isAuthorQuestion(q: AnyQuestion): q is QuestionAuthorResponse {
  return 'explanation' in q
}

const QUESTION_TYPES: QuestionType[] = ['SINGLE_CHOICE', 'MULTIPLE_CHOICE', 'TEXT', 'ESSAY']

function typeLabel(t: QuestionType) {
  switch (t) {
    case 'SINGLE_CHOICE': return 'Single Choice'
    case 'MULTIPLE_CHOICE': return 'Multiple Choice'
    case 'TEXT': return 'Text'
    case 'ESSAY': return 'Essay'
  }
}

interface AnswerBlocksProps {
  question: AnyQuestion
  mode: 'take' | 'edit' | 'review'
  value?: unknown
  onChange?: (value: unknown) => void
  onQuestionChange?: (patch: Partial<QuestionAuthorResponse>) => void
  correctOptionIds?: number[]
  explanation?: string | null
}

export default function AnswerBlocks({
  question,
  mode,
  value,
  onChange,
  onQuestionChange,
  correctOptionIds,
  explanation,
}: AnswerBlocksProps) {
  const isEdit = mode === 'edit'
  const isReview = mode === 'review'
  const options = question.options || []
  const qType = question.question_type

  const selectedSingle = typeof value === 'number' ? value : null
  const selectedMultiple = Array.isArray(value) ? (value as number[]) : []
  const textValue = typeof value === 'string' ? value : ''

  const handleSingleClick = (id: number) => {
    if (isReview) return
    onChange?.(selectedSingle === id ? null : id)
  }

  const handleMultipleToggle = (id: number) => {
    if (isReview) return
    const next = selectedMultiple.includes(id)
      ? selectedMultiple.filter((x) => x !== id)
      : [...selectedMultiple, id]
    onChange?.(next)
  }

  const handleTextChange = (v: string) => {
    if (isReview) return
    onChange?.(v)
  }

  const addOption = () => {
    if (!isEdit || !isAuthorQuestion(question)) return
    if ((question.options?.length || 0) >= 8) return
    const next: OptionAuthorResponse[] = [
      ...(question.options || []),
      {
        id: -Date.now(),
        text: '',
        order_number: (question.options?.length || 0) + 1,
        is_correct: false,
      },
    ]
    onQuestionChange?.({ options: next })
  }

  const removeOption = (idx: number) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const next = (question.options || []).filter((_, i) => i !== idx)
    onQuestionChange?.({
      options: next.map((o, i) => ({ ...o, order_number: i + 1 })) as OptionAuthorResponse[],
    })
  }

  const updateOptionText = (idx: number, text: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const next = (question.options || []).map((o, i) =>
      i === idx ? { ...o, text } : o
    ) as OptionAuthorResponse[]
    onQuestionChange?.({ options: next })
  }

  const toggleOptionCorrect = (idx: number) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const next = (question.options || []).map((o, i) =>
      i === idx ? { ...o, is_correct: !o.is_correct } : o
    ) as OptionAuthorResponse[]
    onQuestionChange?.({ options: next })
  }

  const setPoints = (pts: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const num = Number(pts)
    onQuestionChange?.({ points: Number.isNaN(num) ? 0 : num })
  }

  const setExplanation = (text: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    onQuestionChange?.({ explanation: text })
  }

  const setType = (type: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    onQuestionChange?.({ question_type: type as QuestionType })
  }

  const blockClass = (optId: number, isSelected: boolean) => {
    let base = 'rounded-lg border p-4 transition-colors min-w-[120px]'
    if (isReview) {
      const isCorrectOpt = correctOptionIds?.includes(optId)
      if (isCorrectOpt) base += ' bg-green-50 border-green-500 text-green-700'
      else if (isSelected) base += ' bg-red-50 border-red-500 text-red-700'
      else base += ' bg-background border-input text-foreground'
    } else if (isSelected) {
      base += ' bg-primary/10 border-primary text-primary cursor-pointer'
    } else {
      base += ' bg-background border-input hover:bg-accent cursor-pointer'
    }
    return base
  }

  return (
    <div className="w-full my-4 space-y-4">
      {isEdit && isAuthorQuestion(question) && (
        <div className="flex flex-wrap gap-3 items-center">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Type:</span>
            <Select
              value={question.question_type}
              onChange={(e) => setType(e.target.value)}
              className="w-44"
            >
              {QUESTION_TYPES.map((t) => (
                <SelectItem key={t} value={t}>
                  {typeLabel(t)}
                </SelectItem>
              ))}
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium">Points:</span>
            <Input
              type="number"
              min={0}
              value={question.points}
              onChange={(e) => setPoints(e.target.value)}
              className="w-20"
            />
          </div>
        </div>
      )}

      {(qType === 'SINGLE_CHOICE' || qType === 'MULTIPLE_CHOICE') && (
        <div className="flex flex-wrap gap-3">
          {options.map((opt, idx) => {
            const isSelected =
              qType === 'SINGLE_CHOICE'
                ? selectedSingle === opt.id
                : selectedMultiple.includes(opt.id)

            return (
              <div
                key={opt.id}
                className={isEdit ? 'flex items-start gap-2 w-full' : 'contents'}
              >
                <div
                  className={`${isEdit ? 'flex-1' : 'flex-1 basis-[45%]'} ${blockClass(opt.id, isSelected)}`}
                  onClick={() => {
                    if (qType === 'SINGLE_CHOICE') handleSingleClick(opt.id)
                    else handleMultipleToggle(opt.id)
                  }}
                >
                  <div className="flex items-center gap-2">
                    {qType === 'MULTIPLE_CHOICE' && !isEdit && (
                      <div
                        className={`h-4 w-4 rounded border flex items-center justify-center ${
                          isSelected
                            ? 'bg-primary border-primary'
                            : 'border-muted-foreground'
                        }`}
                      >
                        {isSelected && (
                          <Check className="h-3 w-3 text-primary-foreground" />
                        )}
                      </div>
                    )}
                    {isEdit ? (
                      <Input
                        value={opt.text}
                        onChange={(e) => updateOptionText(idx, e.target.value)}
                        placeholder="Option text..."
                        className="bg-transparent border-none shadow-none focus-visible:ring-0 px-0"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      <span className="text-sm font-medium">{opt.text}</span>
                    )}
                  </div>
                </div>
                {isEdit && isAuthorQuestion(question) && (
                  <>
                    <label className="flex items-center gap-1 text-xs whitespace-nowrap mt-2">
                      <Checkbox
                        checked={(opt as OptionAuthorResponse).is_correct}
                        onCheckedChange={() => toggleOptionCorrect(idx)}
                      />
                      correct?
                    </label>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 mt-1"
                      onClick={() => removeOption(idx)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>
            )
          })}
          {isEdit && (
            <Button
              variant="outline"
              size="sm"
              onClick={addOption}
              disabled={options.length >= 8}
            >
              <Plus className="h-4 w-4 mr-1" /> Add option
            </Button>
          )}
        </div>
      )}

      {(qType === 'TEXT' || qType === 'ESSAY') && (
        <Textarea
          rows={6}
          placeholder="Type your answer here..."
          value={textValue}
          onChange={(e) => handleTextChange(e.target.value)}
          disabled={isReview}
          className="w-full"
        />
      )}

      {qType !== 'SINGLE_CHOICE' &&
        qType !== 'MULTIPLE_CHOICE' &&
        qType !== 'TEXT' &&
        qType !== 'ESSAY' && (
          <div className="p-4 border rounded bg-muted text-muted-foreground text-sm">
            This question type is not yet implemented.
          </div>
        )}

      {isReview && explanation && (
        <div className="rounded-lg border p-3 bg-blue-50 text-blue-800 text-sm">
          <strong>Explanation:</strong> {explanation}
        </div>
      )}

      {isEdit && isAuthorQuestion(question) && (
        <div className="space-y-1">
          <span className="text-sm font-medium">Explanation:</span>
          <Textarea
            rows={3}
            placeholder="Optional explanation shown in review..."
            value={question.explanation || ''}
            onChange={(e) => setExplanation(e.target.value)}
          />
        </div>
      )}
    </div>
  )
}
