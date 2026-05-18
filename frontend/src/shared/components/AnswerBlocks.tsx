import { useState, useCallback, useMemo, useEffect } from 'react'
import { Check, Plus, X, Upload, FileText, Download, ChevronDown, ChevronUp, GripVertical } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Select, SelectItem } from '@/shared/ui/select'
import TypstRender from '@/shared/components/TypstRender'
import { uploadAnswerFileApiV1MediaUploadAnswerPost } from '@/shared/api'
import type {
  QuestionType as QType,
  QuestionResponse,
  QuestionAuthorResponse,
  OptionAuthorResponse,
} from '@/shared/api'

function isAuthorQuestion(q: AnyQuestion): q is QuestionAuthorResponse {
  return 'explanation' in q
}

function ExplanationBlock({ explanation }: { explanation: string }) {
  const [expanded, setExpanded] = useState(false)
  const hasTypst = explanation.includes('$') || explanation.includes('#')
  return (
    <div className="rounded-lg border border-blue-100 bg-blue-50/60 p-3">
      <button
        className="flex items-center gap-2 text-sm font-medium text-blue-700 w-full text-left"
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        Пояснение
      </button>
      {expanded && (
        <div className="mt-2 text-sm text-blue-900">
          {hasTypst ? <TypstRender source={explanation} mode="review" /> : <p className="whitespace-pre-wrap">{explanation}</p>}
        </div>
      )}
    </div>
  )
}

const QUESTION_TYPES: QType[] = ['SINGLE_CHOICE', 'MULTIPLE_CHOICE', 'TEXT', 'ESSAY', 'MATCHING', 'FILE_UPLOAD']
const OPTION_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

function typeLabel(t: QType) {
  switch (t) {
    case 'SINGLE_CHOICE': return 'Один ответ'
    case 'MULTIPLE_CHOICE': return 'Несколько ответов'
    case 'TEXT': return 'Текст'
    case 'ESSAY': return 'Эссе'
    case 'MATCHING': return 'Соответствие'
    case 'FILE_UPLOAD': return 'Файл'
  }
}

type AnyQuestion = QuestionResponse | QuestionAuthorResponse
type MatchingPair = { id: number; term: string; definition: string }
type MatchingAnswer = Record<number, number>

interface AnswerBlocksProps {
  question: AnyQuestion
  mode: 'take' | 'edit' | 'review'
  value?: unknown
  onChange?: (value: unknown) => void
  onQuestionChange?: (patch: Partial<QuestionAuthorResponse>) => void
  onOpenOptionEditor?: (idx: number, currentText: string) => void
  correctOptionIds?: number[]
  explanation?: string | null
}

export default function AnswerBlocks({ question, mode, value, onChange, onQuestionChange, onOpenOptionEditor, correctOptionIds, explanation }: AnswerBlocksProps) {
  const isEdit = mode === 'edit'
  const isReview = mode === 'review'
  const options = question.options || []
  const qType = question.question_type as QType
  const selectedSingle = typeof value === 'number' ? value : null
  const selectedMultiple = Array.isArray(value) ? (value as number[]) : []
  const textValue = typeof value === 'string' ? value : ''
  const questionData = (question.question_data ?? {}) as Record<string, unknown>
  const matchingPairs = questionData.matching_pairs as MatchingPair[] | undefined
  const matchingAnswer = useMemo(() => qType === 'MATCHING' ? ((value as MatchingAnswer) ?? {}) : {}, [qType, value])

  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)
  const fileAnswerUrl = typeof value === 'string' && value.startsWith('http') ? value : null

  useEffect(() => {
    if (fileAnswerUrl && !uploadedUrl && !uploadedFile) setUploadedUrl(fileAnswerUrl)
  }, [fileAnswerUrl, uploadedUrl, uploadedFile])

  const handleSingleClick = (id: number) => { if (!isReview) onChange?.(selectedSingle === id ? null : id) }
  const handleMultipleToggle = (id: number) => {
    if (isReview) return
    onChange?.(selectedMultiple.includes(id) ? selectedMultiple.filter(x => x !== id) : [...selectedMultiple, id])
  }

  const onDrop = useCallback(async (accepted: File[]) => {
    if (isReview || !accepted.length || !onChange) return
    const file = accepted[0]; setUploadedFile(file); setUploading(true)
    try {
      const res = await uploadAnswerFileApiV1MediaUploadAnswerPost({ body: { file: file as Blob } })
      const data = (res.data || res) as Record<string, unknown>
      const url = (data.url as string) || ''
      if (url) { setUploadedUrl(url); onChange(url); setUploading(false); return }
    } catch {}
    const url = URL.createObjectURL(file); setUploadedUrl(url); onChange(url); setUploading(false)
  }, [isReview, onChange])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, disabled: isReview, maxFiles: 1, maxSize: 10 * 1024 * 1024,
    accept: { 'image/*': [], 'application/pdf': [], 'text/plain': [], 'video/*': [], 'audio/*': [] },
  })

  const addOption = () => {
    if (!isEdit || !isAuthorQuestion(question) || (question.options?.length || 0) >= 8) return
    const next: OptionAuthorResponse[] = [...(question.options || []), { id: -Date.now(), text: '', order_number: (question.options?.length || 0) + 1, is_correct: false }]
    onQuestionChange?.({ options: next })
  }
  const removeOption = (idx: number) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    onQuestionChange?.({ options: (question.options || []).filter((_, i) => i !== idx).map((o, i) => ({ ...o, order_number: i + 1 })) as OptionAuthorResponse[] })
  }
  const updateOptionText = (idx: number, text: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    onQuestionChange?.({ options: (question.options || []).map((o, i) => i === idx ? { ...o, text } : o) as OptionAuthorResponse[] })
  }
  const toggleOptionCorrect = (idx: number) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    onQuestionChange?.({ options: (question.options || []).map((o, i) => i === idx ? { ...o, is_correct: !o.is_correct } : o) as OptionAuthorResponse[] })
  }
  const setQuestionData = (patch: Record<string, unknown>) => onQuestionChange?.({ question_data: { ...questionData, ...patch } })
  const addMatchingPair = () => {
    if (!isEdit || (matchingPairs || []).length >= 6) return
    setQuestionData({ matching_pairs: [...(matchingPairs || []), { id: -Date.now(), term: '', definition: '' }] })
  }
  const updateMatchingPair = (idx: number, field: 'term' | 'definition', val: string) => {
    if (!isEdit) return
    const pairs = [...(matchingPairs || [])]; pairs[idx] = { ...pairs[idx], [field]: val }
    setQuestionData({ matching_pairs: pairs })
  }
  const removeMatchingPair = (idx: number) => {
    if (!isEdit) return
    setQuestionData({ matching_pairs: (matchingPairs || []).filter((_, i) => i !== idx) })
  }
  const shuffledDefinitions = useMemo(() => qType !== 'MATCHING' || !matchingPairs ? [] : [...matchingPairs].sort(() => Math.random() - 0.5), [qType, matchingPairs])

  // ── Header: type + points in edit mode ──────────────────────────────────
  const editHeader = isEdit && isAuthorQuestion(question) && (
    <div className="flex items-center gap-4 text-sm flex-wrap">
      <label className="flex items-center gap-2 text-muted-foreground shrink-0">
        <span className="text-sm">Тип:</span>
        <Select value={question.question_type} onChange={(e) => onQuestionChange?.({ question_type: e.target.value as QType })} className="h-9 text-sm w-52">
          {QUESTION_TYPES.map(t => <SelectItem key={t} value={t}>{typeLabel(t)}</SelectItem>)}
        </Select>
      </label>
      <label className="flex items-center gap-2 text-muted-foreground shrink-0">
        <span className="text-sm">Баллов:</span>
        <Input type="number" min={0} value={isAuthorQuestion(question) ? question.points : 0} onChange={e => onQuestionChange?.({ points: Number(e.target.value) || 0 })} className="h-9 w-16 text-sm text-center" />
      </label>
    </div>
  )

  // ── SINGLE / MULTIPLE CHOICE ──────────────────────────────────────────────
  if (qType === 'SINGLE_CHOICE' || qType === 'MULTIPLE_CHOICE') {
    if (isEdit) {
      return (
        <div className="space-y-3">
          {editHeader}
          <div className="space-y-2">
            {options.map((opt, idx) => {
              const isCorrect = (opt as OptionAuthorResponse).is_correct
              return (
                <div
                  key={opt.id}
                  className={`group flex items-start gap-2 rounded-lg border px-3 py-2.5 transition-colors ${
                    isCorrect ? 'border-green-400 bg-green-50' : 'border-border bg-background hover:bg-muted/20'
                  }`}
                >
                  {/* Letter badge */}
                  <span className="w-6 h-6 rounded flex items-center justify-center text-xs font-bold text-muted-foreground bg-muted shrink-0 mt-0.5">
                    {OPTION_LETTERS[idx]}
                  </span>

                  {/* Option content: rendered Typst or placeholder */}
                  <div
                    className="flex-1 min-w-0 min-h-[24px] cursor-pointer"
                    onClick={() => onOpenOptionEditor?.(idx, opt.text)}
                  >
                    {opt.text
                      ? <TypstRender source={opt.text} mode="take" compact />
                      : <span className="text-sm text-muted-foreground/50 italic">
                          Вариант {OPTION_LETTERS[idx]} — нажмите для редактирования
                        </span>
                    }
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 shrink-0 mt-0.5">
                    <button
                      onClick={() => onOpenOptionEditor?.(idx, opt.text)}
                      title="Редактировать"
                      className="opacity-0 group-hover:opacity-100 transition-opacity rounded px-1.5 py-0.5 text-xs text-muted-foreground hover:bg-muted"
                    >
                      Изм.
                    </button>
                    <button
                      onClick={() => toggleOptionCorrect(idx)}
                      title={isCorrect ? 'Убрать правильный' : 'Отметить правильным'}
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                        isCorrect ? 'bg-green-500 border-green-500 text-white' : 'border-muted-foreground/30 hover:border-green-400'
                      }`}
                    >
                      {isCorrect && <Check className="h-3 w-3" />}
                    </button>
                    <button onClick={() => removeOption(idx)} className="text-muted-foreground/30 hover:text-destructive">
                      <X className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              )
            })}
            {options.length < 8 && (
              <button
                onClick={addOption}
                className="w-full flex items-center gap-2 rounded-lg border border-dashed border-muted-foreground/25 px-3 py-2 text-sm text-muted-foreground hover:border-primary/50 hover:text-primary transition-colors"
              >
                <Plus className="h-4 w-4" />
                Добавить вариант
              </button>
            )}
          </div>
          {isAuthorQuestion(question) && (
            <div>
              <p className="text-xs text-muted-foreground mb-1">Пояснение (необязательно)</p>
              <Textarea rows={2} placeholder="Показывается студенту после проверки..." value={question.explanation || ''} onChange={e => onQuestionChange?.({ explanation: e.target.value })} className="text-sm resize-none" />
            </div>
          )}
        </div>
      )
    }

    // take / review
    return (
      <div className="space-y-2">
        {options.map((opt, idx) => {
          const isSelected = qType === 'SINGLE_CHOICE' ? selectedSingle === opt.id : selectedMultiple.includes(opt.id)
          const isCorrectOpt = isReview && correctOptionIds?.includes(opt.id)
          const isWrongSelected = isReview && isSelected && !isCorrectOpt
          return (
            <div
              key={opt.id}
              onClick={() => qType === 'SINGLE_CHOICE' ? handleSingleClick(opt.id) : handleMultipleToggle(opt.id)}
              className={`flex items-center gap-3 rounded-xl border-2 px-4 py-3 transition-all select-none ${
                isReview
                  ? isCorrectOpt ? 'border-green-500 bg-green-50' : isWrongSelected ? 'border-red-400 bg-red-50' : 'border-border bg-background'
                  : isSelected ? 'border-primary bg-primary/8 cursor-pointer' : 'border-border bg-background hover:border-primary/40 hover:bg-muted/30 cursor-pointer'
              }`}
            >
              <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold shrink-0 transition-colors ${
                isReview ? isCorrectOpt ? 'bg-green-500 text-white' : isWrongSelected ? 'bg-red-400 text-white' : 'bg-muted text-muted-foreground'
                : isSelected ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                {OPTION_LETTERS[idx]}
              </span>
              <div className="flex-1 min-w-0">
                <TypstRender source={opt.text || ''} mode="take" compact />
              </div>
              {isReview && isCorrectOpt && <Check className="h-4 w-4 text-green-600 shrink-0" />}
              {isReview && isWrongSelected && <X className="h-4 w-4 text-red-500 shrink-0" />}
            </div>
          )
        })}
        {isReview && explanation && <ExplanationBlock explanation={explanation} />}
      </div>
    )
  }

  // ── TEXT / ESSAY ──────────────────────────────────────────────────────────
  if (qType === 'TEXT' || qType === 'ESSAY') {
    if (isEdit && isAuthorQuestion(question)) {
      return (
        <div className="space-y-3">
          {editHeader}
          <div className="rounded-lg border border-dashed border-muted-foreground/30 bg-muted/20 p-4 text-center text-sm text-muted-foreground">
            Студент введёт ответ в текстовое поле
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Правильный ответ (для автопроверки)</p>
            <Input value={question.correct_answer || ''} onChange={e => onQuestionChange?.({ correct_answer: e.target.value })} placeholder="Ожидаемый ответ..." className="text-sm" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground mb-1">Пояснение</p>
            <Textarea rows={2} placeholder="Необязательное пояснение..." value={question.explanation || ''} onChange={e => onQuestionChange?.({ explanation: e.target.value })} className="text-sm resize-none" />
          </div>
        </div>
      )
    }
    return (
      <div className="space-y-3">
        <Textarea rows={5} placeholder="Введите ответ..." value={textValue} onChange={e => onChange?.(e.target.value)} disabled={isReview} className="w-full resize-none" />
        {isReview && explanation && <ExplanationBlock explanation={explanation} />}
      </div>
    )
  }

  // ── MATCHING ──────────────────────────────────────────────────────────────
  if (qType === 'MATCHING') {
    if (isEdit) {
      return (
        <div className="space-y-3">
          {editHeader}
          <div className="space-y-2">
            {matchingPairs?.map((pair, idx) => (
              <div key={pair.id} className="flex items-center gap-2">
                <GripVertical className="h-4 w-4 text-muted-foreground shrink-0" />
                <Input value={pair.term} onChange={e => updateMatchingPair(idx, 'term', e.target.value)} placeholder="Термин..." className="flex-1 h-8 text-sm" />
                <span className="text-muted-foreground text-sm">→</span>
                <Input value={pair.definition} onChange={e => updateMatchingPair(idx, 'definition', e.target.value)} placeholder="Определение..." className="flex-1 h-8 text-sm" />
                <button onClick={() => removeMatchingPair(idx)} className="text-muted-foreground/40 hover:text-destructive"><X className="h-4 w-4" /></button>
              </div>
            ))}
            {(!matchingPairs || matchingPairs.length < 6) && (
              <Button variant="outline" size="sm" onClick={addMatchingPair} className="w-full">
                <Plus className="h-4 w-4 mr-1" /> Добавить пару
              </Button>
            )}
          </div>
        </div>
      )
    }
    return (
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Термины</p>
          {matchingPairs?.map(pair => (
            <div key={pair.id} className="rounded-lg border bg-background p-3 text-sm font-medium">{pair.term}</div>
          ))}
        </div>
        <div className="space-y-2">
          <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Соответствия</p>
          {shuffledDefinitions.map(def => {
            const selectedTerm = Object.entries(matchingAnswer).find(([_, v]) => v === def.id)
            return (
              <div key={def.id} className={`rounded-lg border p-3 text-sm ${isReview && selectedTerm ? 'bg-green-50 border-green-400' : 'bg-background'}`}>
                <div className="flex items-center gap-2">
                  <span className="flex-1">{def.definition}</span>
                  {!isReview && (
                    <select className="text-xs border rounded px-2 py-1 bg-background" value={selectedTerm?.[0] ?? ''} onChange={e => onChange?.({ ...matchingAnswer, [Number(e.target.value)]: def.id })}>
                      <option value="">—</option>
                      {matchingPairs?.map(p => <option key={p.id} value={p.id}>{p.term}</option>)}
                    </select>
                  )}
                </div>
              </div>
            )
          })}
        </div>
        {isReview && explanation && <div className="col-span-2"><ExplanationBlock explanation={explanation} /></div>}
      </div>
    )
  }

  // ── FILE_UPLOAD ───────────────────────────────────────────────────────────
  if (qType === 'FILE_UPLOAD') {
    if (isEdit) {
      return (
        <div className="space-y-3">
          {editHeader}
          <div className="rounded-lg border-2 border-dashed border-muted-foreground/25 p-5 text-center text-sm text-muted-foreground">
            <FileText className="h-6 w-6 mx-auto mb-2 text-muted-foreground/50" />
            <p>Студент загружает файл-ответ</p>
          </div>
        </div>
      )
    }
    return (
      <div className="space-y-3">
        {uploading ? (
          <div className="rounded-lg border p-4 flex items-center gap-3 text-muted-foreground">
            <FileText className="h-6 w-6" /><span className="text-sm">Загрузка...</span>
          </div>
        ) : uploadedUrl ? (
          <div className="rounded-lg border p-4 flex items-center gap-3">
            <FileText className="h-6 w-6 text-primary" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{uploadedFile?.name || 'Файл'}</p>
              {uploadedFile && <p className="text-xs text-muted-foreground">{(uploadedFile.size / 1024).toFixed(1)} KB</p>}
            </div>
            {!isReview && <Button variant="ghost" size="sm" onClick={() => { setUploadedFile(null); setUploadedUrl(null); onChange?.(null) }}><X className="h-4 w-4" /></Button>}
            <Button variant="outline" size="sm" asChild><a href={uploadedUrl} download={uploadedFile?.name} target="_blank" rel="noreferrer"><Download className="h-4 w-4 mr-1" />Скачать</a></Button>
          </div>
        ) : (
          <div {...getRootProps()} className={`rounded-xl border-2 border-dashed p-7 text-center cursor-pointer transition-colors ${isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25 hover:border-muted-foreground/50'} ${isReview ? 'pointer-events-none opacity-60' : ''}`}>
            <input {...getInputProps()} />
            <Upload className="h-7 w-7 mx-auto mb-2 text-muted-foreground" />
            <p className="text-sm font-medium">{isDragActive ? 'Отпустите...' : isReview ? 'Файл не загружен' : 'Перетащите или кликните'}</p>
            <p className="text-xs text-muted-foreground mt-1">До 10 МБ</p>
          </div>
        )}
      </div>
    )
  }

  return <div className="p-4 border rounded bg-muted text-muted-foreground text-sm">Тип вопроса не поддерживается.</div>
}
