import {useState} from 'react'
import {useNavigate, useParams} from 'react-router-dom'
import {useCreateTest} from '@/features/test-management/api/useTests'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Label} from '@/shared/ui/label'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'

export default function EditorPage() {
  const {testId} = useParams()
  const navigate = useNavigate()
  const create = useCreateTest()
  const [form, setForm] = useState({title: '', description: '', is_public: false, time_limit_minutes: '' as string | number})

  if (testId) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <h1 className="text-2xl font-bold mb-4">Редактор #{testId}</h1>
        <p className="text-muted-foreground">Редактор вопросов в разработке.</p>
      </div>
    )
  }

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    create.mutate({...form, time_limit_minutes: form.time_limit_minutes ? Number(form.time_limit_minutes) : undefined} as any, {
      onSuccess: (res: any) => {
        const id = res.data?.id || res.id
        if (id) navigate(`/editor/${id}`)
      }
    })
  }

  return (
    <div className="max-w-xl mx-auto p-6">
      <Card>
        <CardHeader><CardTitle>Новый тест</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={submit} className="space-y-4">
            <div>
              <Label>Название</Label>
              <Input value={form.title} onChange={e => setForm(s => ({...s, title: e.target.value}))} required />
            </div>
            <div>
              <Label>Описание</Label>
              <Input value={form.description} onChange={e => setForm(s => ({...s, description: e.target.value}))} />
            </div>
            <div>
              <Label>Ограничение по времени (мин)</Label>
              <Input type="number" value={form.time_limit_minutes} onChange={e => setForm(s => ({...s, time_limit_minutes: e.target.value}))} />
            </div>
            <Button type="submit" className="w-full" disabled={create.isPending}>{create.isPending?'Создание...':'Создать тест'}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
