import {useNavigate} from 'react-router-dom'
import {useMyTests} from '@/features/test-management/api/useTests'
import {Button} from '@/shared/ui/button'
import {Loader} from '@/shared/ui/loader'

export default function StatsPage() {
  const navigate = useNavigate()
  const {data, isLoading} = useMyTests()

  if (isLoading) return <Loader />

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Мои тесты</h1>
      {data?.data?.map((t: any) => (
        <div key={t.id} className="border rounded p-4 flex items-center justify-between" onClick={() => navigate(`/editor/${t.id}`)}>
          <div>
            <p className="font-semibold">{t.title}</p>
            <p className="text-sm text-muted-foreground">{t.description}</p>
          </div>
          <Button variant="outline" size="sm">Редактировать</Button>
        </div>
      ))}
    </div>
  )
}
