import {useState} from 'react'
import {useNavigate, useParams} from 'react-router-dom'
import {useTestDetail, useCreateTest, useUpdateTest, useAddQuestion, useDeleteQuestion} from '@/features/test-management/api/useTests'
import {useUserStore} from '@/entities/user/model/store'
import {QuestionFormData} from '@/widgets/question-editor/ui/QuestionEditorWidget'
import QuestionEditorWidget from '@/widgets/question-editor/ui/QuestionEditorWidget'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Label} from '@/shared/ui/label'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
import {Badge} from '@/shared/ui/badge'
import {Loader} from '@/shared/ui/loader'

export default function EditorPage() {
  const {testId} = useParams()
  const navigate = useNavigate()
  const user = useUserStore(s => s.user)
  const id = Number(testId)

  const {data: test, isLoading} = useTestDetail(id)
  const create = useCreateTest()
  const update = useUpdateTest(id)
  const addQuestion = useAddQuestion(id)
  const deleteQuestion = useDeleteQuestion()

  const [editingQuestion, setEditingQuestion] = useState<QuestionFormData | null>(null)
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  const [meta, setMeta] = useState({title: '', description: '', is_public: false, time_limit_minutes: '' as string | number})

  if (testId && isLoading) return <Loader />
  if (testId && test?.data && (test.data as any).author_id !== user?.id) {
    return <div className="p-6 text-red-500">Нет доступа к редактированию этого теста.</div>
  }

  if (testId) {
    const questions = (test?.data as any)?.questions || []
    return (
      <div className="max-w-5xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-bold">{(test?.data as any)?.title}</h1>
        <p className="text-muted-foreground">{(test?.data as any)?.description}</p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1 space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Вопросы</h2>
              <Button size="sm" onClick={() => setEditingQuestion(null)}>+</Button>
            </div>
            {questions.map((q: any, idx: number) => (
              <div key={q.id} className={`p-2 border rounded cursor-pointer ${activeIndex === idx ? 'bg-gray-100' : ''}`} onClick={() => {setActiveIndex(idx); setEditingQuestion(q)}}>
                <p className="text-sm truncate">{idx + 1}. {q.text.slice(0, 40)}</p>
              </div>
            ))}
          </div>
          <div className="md:col-span-2">
            {editingQuestion === null ? (
              <Card>
                <CardContent className="p-4">
                  <Button onClick={() => setEditingQuestion({question_type: 'single_choice', text: '', points: 1, explanation: null, correct_answer: null, image_url: null, options: []} as any)}>Создать новый вопрос</Button>
                </CardContent>
              </Card>
            ) : (
              <QuestionEditorWidget
                initialData={editingQuestion}
                onSave={(data) => {
                  if ((editingQuestion as any)?.id) {
                    // update via mutation (TODO once hook available)
                    setEditingQuestion(null)
                  } else {
                    addQuestion.mutate(data as any, {onSuccess: () => setEditingQuestion(null)})
                  }
                }}
                onCancel={() => setEditingQuestion(null)}
              />
            )}
          </div>
        </div>
      </div>
    )
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    create.mutate({...meta, time_limit_minutes: meta.time_limit_minutes ? Number(meta.time_limit_minutes) : undefined} as any, {
      onSuccess: (res: any) => {
        const newId = res.data?.id || res.id
        if (newId) navigate(`/editor/${newId}`)
      }
    })
  }

  return (
    <div className="max-w-xl mx-auto p-6">
      <Card>
        <CardHeader><CardTitle>Новый тест</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-4">
            <div><Label>Название</Label><Input value={meta.title} onChange={e => setMeta(s => ({...s, title: e.target.value}))} required /></div>
            <div><Label>Описание</Label><Input value={meta.description} onChange={e => setMeta(s => ({...s, description: e.target.value}))} /></div>
            <div><Label>Ограничение по времени (мин)</Label><Input type="number" value={meta.time_limit_minutes} onChange={e => setMeta(s => ({...s, time_limit_minutes: e.target.value}))} /></div>
            <Button type="submit" className="w-full" disabled={create.isPending}>{create.isPending ? 'Создание...' : 'Создать тест'}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
