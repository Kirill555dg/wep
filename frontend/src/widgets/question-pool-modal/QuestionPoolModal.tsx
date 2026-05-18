import { useState, useEffect } from 'react'
import { Search, Loader2, Plus } from 'lucide-react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/shared/ui/dialog'
import { Button } from '@/shared/ui/button'
import { listQuestionPoolApiV1TestsQuestionsPoolGet,
  addQuestionFromPoolApiV1TestsTestIdQuestionsQuestionIdFromPoolPost,
  client } from '@/shared/api'
import type { QuestionPoolResponse, QuestionAuthorResponse } from '@/shared/api'
import { useToast } from '@/shared/hooks/useToast'
import { InlineLoading } from '@/shared/components/ui/loading'
import { EmptyState } from '@/shared/components/ui/empty-state'

interface QuestionPoolModalProps {
  testId: number
  open: boolean
  onClose: () => void
  onAdded: (question?: QuestionAuthorResponse) => void
}

export default function QuestionPoolModal({ testId, open, onClose, onAdded }: QuestionPoolModalProps) {
  const [search, setSearch] = useState('')
  const { toastSuccess, toastError } = useToast()

  const { data, isLoading } = useQuery({
    queryKey: ['question-pool', search],
    queryFn: () =>
      listQuestionPoolApiV1TestsQuestionsPoolGet({
        client,
        query: { query: search || undefined, skip: 0, limit: 50 },
      }),
    enabled: open,
  })

  const questions: QuestionPoolResponse[] = (data?.data as QuestionPoolResponse[] | undefined) ?? []

  const addMutation = useMutation({
    mutationFn: (questionId: number) =>
      addQuestionFromPoolApiV1TestsTestIdQuestionsQuestionIdPost({
        client,
        path: { test_id: testId, question_id: questionId },
      }),
    onSuccess: (res) => {
      toastSuccess('Вопрос добавлен')
      onAdded(res.data as QuestionAuthorResponse | undefined)
    },
    onError: () => {
      toastError('Не удалось добавить вопрос')
    },
  })

  return (
    <Dialog open={open} onOpenChange={(val) => !val && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Добавить вопрос из пула</DialogTitle>
        </DialogHeader>

        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Поиск по тексту вопроса..."
            className="w-full h-10 pl-10 pr-4 rounded-md border border-input bg-background text-sm focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 min-h-[200px]">
          {isLoading && <InlineLoading />}

          {!isLoading && questions.length === 0 && (
            <EmptyState
              icon="search"
              title="Вопросы не найдены"
              description="Создайте новый вопрос или измените поисковый запрос"
            />
          )}

          {questions.map((q) => (
            <div
              key={q.id}
              className="flex items-center justify-between p-3 rounded-lg border hover:bg-gray-50 transition-colors"
            >
              <div className="flex-1 min-w-0 mr-4">
                <p className="text-sm font-medium truncate">{q.text}</p>
                <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                  <span className="px-1.5 py-0.5 rounded bg-gray-100">{q.question_type}</span>
                  <span>{q.points} баллов</span>
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => addMutation.mutate(q.id)}
                disabled={addMutation.isPending}
              >
                {addMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <>
                    <Plus className="w-4 h-4 mr-1" />
                    Добавить
                  </>
                )}
              </Button>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
