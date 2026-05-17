import {useState} from 'react'
import {useNavigate, useParams} from 'react-router-dom'
import {useTestDetail, useCreateTest, useUpdateTest, useAddQuestion, useUpdateQuestion, useDeleteQuestion} from '@/features/test-management/api/useTests'
import {useUserStore} from '@/entities/user/model/store'
import {QuestionFormData} from '@/widgets/question-editor/ui/QuestionEditorWidget'
import QuestionEditorWidget from '@/widgets/question-editor/ui/QuestionEditorWidget'
import TagInput from '@/widgets/search-bar/ui/TagInput'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Label} from '@/shared/ui/label'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
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
  const updateQuestion = useUpdateQuestion(id, (editingQuestion as any)?.id ?? 0)
  const deleteQuestion = useDeleteQuestion()

  const [editingQuestion, setEditingQuestion] = useState<QuestionFormData | null>(null)
  const [activeIndex, setActiveIndex] = useState<number | null>(null)

  const [meta, setMeta] = useState({title: '', description: '', is_public: false, time_limit_minutes: '' as string | number, tag_names: [] as string[]})

  if (testId && isLoading) return <Loader />
  if (testId && (test as any)?.data && (test as any).data.author_id !== user?.id) {
    return <div className="p-6 text-red-500">Нет доступа к редактированию этого теста.</div>
  }

  if (testId) {
    const t = (test as any)?.data
    const questions = t?.questions || []
    return (
      <div className="max-w-5xl mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-bold">{t?.title}</h1>
        <Card>
          <CardContent className="p-4 space-y-3">
            <div><Label>Название</Label><Input value={meta.title || t?.title || ''} onChange={e => setMeta(s => ({...s, title: e.target.value}))} /></div>
            <div><Label>Описание</Label><Input value={meta.description || t?.description || ''} onChange={e => setMeta(s => ({...s, description: e.target.value}))} /></div>
            <div><Label>Теги</Label><TagInput selected={meta.tag_names} onChange={tags => setMeta(s => ({...s, tag_names: tags}))} /></div>
            <Button onClick={() => update.mutate(meta)} disabled={update.isPending}>{update.isPending ? 'Сохранение...' : 'Сохранить тест'}</Button>
          </CardContent>
        </Card>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="md:col-span-1 space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Вопросы</h2>
              <Button size="sm" onClick={() => {setEditingQuestion(null); setActiveIndex(null)}}>+</Button>
            </div>
            {questions.map((q: any, idx: number) => (
              <div key={q.id} className={`p-2 border rounded cursor-pointer ${activeIndex === idx ? 'bg-gray-100' : ''}`} onClick={() => {setActiveIndex(idx); setEditingQuestion(q)}}>
                <div className="flex items-center justify-between">
                  <p className="text-sm truncate">{idx + 1}. {q.text.slice(0, 40)}</p>
                  <Button variant="ghost" size="sm" className="text-red-500" onClick={(e) => {e.stopPropagation(); deleteQuestion.mutate({testId: id, questionId: q.id})}}>Удалить</Button>
                </div>
              </div>
            ))}
          </div>
          <div className="md:col-span-2">
            {editingQuestion !== null && (
              <QuestionEditorWidget
                initialData={editingQuestion}
                onSave={(data) => {
                  if ((editingQuestion as any)?.id) {
                    updateQuestion.mutate(data as any, {onSuccess: () => setEditingQuestion(null)})
                  } else {
                    addQuestion.mutate(data as any, {onSuccess: () => setEditingQuestion(null)})
                  }
                }}
                onCancel={() => setEditingQuestion(null)}
                onDelete={(editingQuestion as any)?.id ? () => {
                  deleteQuestion.mutate({testId: id, questionId: (editingQuestion as any).id}, {
                    onSuccess: () => { setEditingQuestion(null); setActiveIndex(null) }
                  })
                } : undefined}
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
            <div><Label>Теги</Label><TagInput selected={meta.tag_names} onChange={tags => setMeta(s => ({...s, tag_names: tags}))} /></div>
            <Button type="submit" className="w-full" disabled={create.isPending}>{create.isPending ? 'Создание...' : 'Создать тест'}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
