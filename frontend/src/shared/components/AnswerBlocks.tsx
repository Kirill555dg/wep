import { useState, useCallback, useMemo, useEffect } from 'react'
import { Check, Plus, X, Upload, FileText, Download, ChevronDown, ChevronUp } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

import { Button } from '@/shared/ui/button'
import { Input } from '@/shared/ui/input'
import { Textarea } from '@/shared/ui/textarea'
import { Checkbox } from '@/shared/ui/checkbox'
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
  const hasTypst = explanation.includes('$') || explanation.includes('#') || explanation.includes('```')

  return (
    <div className="rounded-lg border p-3 bg-blue-50 text-blue-800">
      <button
        className="flex items-center gap-2 text-sm font-medium w-full text-left hover:opacity-80"
        onClick={() => setExpanded((v) => !v)}
      >
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        <span>Объяснение</span>
      </button>
      {expanded && (
        <div className="mt-2 text-sm">
          {hasTypst ? (
            <TypstRender source={explanation} mode="review" />
          ) : (
            <p className="whitespace-pre-wrap">{explanation}</p>
          )}
        </div>
      )}
    </div>
  )
}

const QUESTION_TYPES: QType[] = [
  'SINGLE_CHOICE',
  'MULTIPLE_CHOICE',
  'TEXT',
  'ESSAY',
  'MATCHING',
  'FILE_UPLOAD',
]

type AnyQuestion = QuestionResponse | QuestionAuthorResponse

function typeLabel(t: QType) {
  switch (t) {
    case 'SINGLE_CHOICE': return 'Single Choice'
    case 'MULTIPLE_CHOICE': return 'Multiple Choice'
    case 'TEXT': return 'Text'
    case 'ESSAY': return 'Essay'
    case 'MATCHING': return 'Matching'
    case 'FILE_UPLOAD': return 'File Upload'
  }
}

type MatchingPair = { id: number; term: string; definition: string }

type MatchingAnswer = Record<number, number>

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
  const qType = question.question_type as QType

  const selectedSingle = typeof value === 'number' ? value : null
  const selectedMultiple = Array.isArray(value) ? (value as number[]) : []
  const textValue = typeof value === 'string' ? value : ''

  const questionData = (question.question_data ?? {}) as Record<string, unknown>
  const matchingPairs = (questionData.matching_pairs as MatchingPair[] | undefined)
  const matchingAnswer = useMemo(() => {
    if (qType !== 'MATCHING') return {} as Record<number, number>
    const v = value as MatchingAnswer | undefined
    return v ?? {}
  }, [qType, value])

  const [uploadedFile, setUploadedFile] = useState<File | null>(null)
  const [uploadedUrl, setUploadedUrl] = useState<string | null>(null)
  const [uploading, setUploading] = useState(false)

  const fileAnswerUrl = typeof value === 'string' && value.startsWith('http') ? value : null

  useEffect(() => {
    if (fileAnswerUrl && !uploadedUrl && !uploadedFile) {
      setUploadedUrl(fileAnswerUrl)
    }
  }, [fileAnswerUrl, uploadedUrl, uploadedFile])

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

  const handleMatchingChange = (termId: number, defId: number) => {
    if (isReview) return
    onChange?.({ ...matchingAnswer, [termId]: defId })
  }

  const onDrop = useCallback(
    async (accepted: File[]) => {
      if (isReview || !accepted.length || !onChange) return
      const file = accepted[0]
      setUploadedFile(file)
      setUploading(true)
      try {
        const res = await uploadAnswerFileApiV1MediaUploadAnswerPost({ body: { file: file as Blob } })
        const data = (res.data || res) as Record<string, unknown>
        const url = (data.url as string) || ''
        if (url) {
          setUploadedUrl(url)
          onChange(url)
          setUploading(false)
          return
        }
      } catch {
        // fallback to blob URL
      }
      const url = URL.createObjectURL(file)
      setUploadedUrl(url)
      onChange(url)
      setUploading(false)
    },
    [isReview, onChange],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled: isReview,
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    accept: {
      'image/*': [],
      'application/pdf': [],
      'application/msword': [],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': [],
      'text/plain': [],
      'video/*': [],
      'audio/*': [],
    },
  })

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
    onQuestionChange?.({ question_type: type as QType })
  }

  const setQuestionData = (patch: Record<string, unknown>) => {
    onQuestionChange?.({ question_data: { ...questionData, ...patch } })
  }

  const addMatchingPair = () => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const pairs = matchingPairs || []
    if (pairs.length >= 6) return
    const next = [
      ...pairs,
      { id: -Date.now(), term: '', definition: '' },
    ]
    setQuestionData({ matching_pairs: next })
  }

  const updateMatchingPair = (idx: number, field: 'term' | 'definition', value: string) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const pairs = [...(matchingPairs || [])]
    pairs[idx] = { ...pairs[idx], [field]: value }
    setQuestionData({ matching_pairs: pairs })
  }

  const removeMatchingPair = (idx: number) => {
    if (!isEdit || !isAuthorQuestion(question)) return
    const pairs = (matchingPairs || []).filter((_, i) => i !== idx)
    setQuestionData({ matching_pairs: pairs })
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

  const shuffledDefinitions = useMemo(() => {
    if (qType !== 'MATCHING' || !matchingPairs) return []
    return [...matchingPairs].sort(() => Math.random() - 0.5)
  }, [qType, matchingPairs])

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
                      <TypstRender source={opt.text} mode="take" />
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

      {qType === 'MATCHING' && (
        <div className="space-y-4">
          {isEdit ? (
            <div className="space-y-3">
              {(!matchingPairs || matchingPairs.length === 0) && (
                <p className="text-sm text-muted-foreground">
                  Add matching pairs (term → definition).
                </p>
              )}
              {matchingPairs?.map((pair, idx) => (
                <div key={pair.id} className="flex items-start gap-2">
                  <div className="flex-1 space-y-1">
                    <span className="text-xs text-muted-foreground">Term</span>
                    <Input
                      value={pair.term}
                      onChange={(e) => updateMatchingPair(idx, 'term', e.target.value)}
                      placeholder="Enter term..."
                    />
                  </div>
                  <div className="flex-1 space-y-1">
                    <span className="text-xs text-muted-foreground">Definition</span>
                    <Input
                      value={pair.definition}
                      onChange={(e) => updateMatchingPair(idx, 'definition', e.target.value)}
                      placeholder="Enter definition..."
                    />
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-10 w-10 mt-5"
                    onClick={() => removeMatchingPair(idx)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              {(!matchingPairs || matchingPairs.length < 6) && (
                <Button variant="outline" size="sm" onClick={addMatchingPair}>
                  <Plus className="h-4 w-4 mr-1" /> Add pair
                </Button>
              )}
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-3">
                <p className="text-sm font-medium text-muted-foreground">Terms</p>
                {matchingPairs?.map((pair) => (
                  <div
                    key={pair.id}
                    className="rounded-lg border bg-background p-3 text-sm font-medium"
                  >
                    {pair.term}
                  </div>
                ))}
              </div>
              <div className="space-y-3">
                <p className="text-sm font-medium text-muted-foreground">Matches</p>
                {shuffledDefinitions.map((def) => {
                  const selectedTerm = Object.entries(matchingAnswer).find(
                    ([_, v]) => v === def.id,
                  )
                  return (
                    <div
                      key={def.id}
                      className={`rounded-lg border p-3 text-sm ${
                        isReview
                          ? selectedTerm
                            ? Number(selectedTerm[0]) ===
                              matchingPairs?.find((p) => p.definition === def.definition)?.id
                              ? 'bg-green-50 border-green-500'
                              : 'bg-red-50 border-red-500'
                            : 'bg-background'
                          : 'bg-background'
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <span className="flex-1">{def.definition}</span>
                        {!isReview && (
                          <select
                            className="text-xs border rounded px-2 py-1 bg-background"
                            value={selectedTerm?.[0] ?? ''}
                            onChange={(e) =>
                              handleMatchingChange(
                                Number(e.target.value),
                                def.id,
                              )
                            }
                          >
                            <option value="">—</option>
                            {matchingPairs?.map((p) => (
                              <option key={p.id} value={p.id}>
                                {p.term}
                              </option>
                            ))}
                          </select>
                        )}
                        {isReview && selectedTerm && (
                          <span className="text-xs text-muted-foreground">
                            → {matchingPairs?.find((p) => p.id === Number(selectedTerm[0]))?.term}
                          </span>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}

      {qType === 'FILE_UPLOAD' && (
        <div className="space-y-3">
          {isEdit ? (
            <div className="rounded-lg border-2 border-dashed p-6 text-center text-sm text-muted-foreground">
              <FileText className="h-8 w-8 mx-auto mb-2" />
              <p>File upload is enabled for this question</p>
              <p className="text-xs mt-1">Students will be able to upload images, PDFs, audio, video, text</p>
            </div>
          ) : uploading ? (
            <div className="rounded-lg border p-4 flex items-center gap-3 text-muted-foreground">
              <FileText className="h-8 w-8" />
              <span className="text-sm">Uploading...</span>
            </div>
          ) : uploadedUrl || fileAnswerUrl ? (
            <div className="rounded-lg border p-4 flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">
                  {uploadedFile?.name || 'Uploaded file'}
                </p>
                {uploadedFile && (
                  <p className="text-xs text-muted-foreground">
                    {(uploadedFile.size / 1024).toFixed(1)} KB
                  </p>
                )}
              </div>
              {!isReview && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setUploadedFile(null)
                    setUploadedUrl(null)
                    onChange?.(null)
                  }}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
              <Button variant="outline" size="sm" asChild>
                <a href={uploadedUrl || fileAnswerUrl || '#'} download={uploadedFile?.name} target="_blank" rel="noreferrer">
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </a>
              </Button>
            </div>
          ) : (
            <div
              {...getRootProps()}
              className={`rounded-lg border-2 border-dashed p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary bg-primary/5'
                  : 'border-muted-foreground/25 hover:border-muted-foreground/50'
              } ${isReview ? 'pointer-events-none opacity-60' : ''}`}
            >
              <input {...getInputProps()} />
              <Upload className="h-8 w-8 mx-auto mb-2 text-muted-foreground" />
              {isDragActive ? (
                <p className="text-sm font-medium">Drop file here...</p>
              ) : (
                <>
                  <p className="text-sm font-medium">
                    {isReview ? 'No file uploaded' : 'Drop file here or click to browse'}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Max 10 MB — images, PDF, documents, audio, video
                  </p>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {qType !== 'SINGLE_CHOICE' &&
        qType !== 'MULTIPLE_CHOICE' &&
        qType !== 'TEXT' &&
        qType !== 'ESSAY' &&
        qType !== 'MATCHING' &&
        qType !== 'FILE_UPLOAD' && (
          <div className="p-4 border rounded bg-muted text-muted-foreground text-sm">
            This question type is not yet implemented.
          </div>
        )}

      {isReview && explanation && (
        <ExplanationBlock explanation={explanation} />
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
