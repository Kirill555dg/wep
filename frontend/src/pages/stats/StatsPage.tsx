import {useNavigate} from 'react-router-dom'
import {useMyTests} from '@/features/test-management/api/useTests'
import {getTestStatsApiV1StatsTestsTestIdGet} from '@/shared/api/client/stats'
import {Button} from '@/shared/ui/button'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
import {Loader} from '@/shared/ui/loader'
import {Badge} from '@/shared/ui/badge'

export default function StatsPage() {
  const navigate = useNavigate()
  const {data, isLoading} = useMyTests()

  if (isLoading) return <Loader />

  const tests = (data as any)?.data || []

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Мои тесты</h1>
      {tests.map((t: any) => (
        <Card key={t.id} className="cursor-pointer" onClick={() => navigate(`/editor/${t.id}`)}>
          <CardHeader className="pb-2">
            <CardTitle className="text-lg">{t.title}</CardTitle>
          </CardHeader>
          <CardContent className="flex items-center justify-between">
            <div className="flex gap-2">
              <Badge variant="outline">Вопросов: {t.questions_count}</Badge>
              <Badge variant={t.is_public ? 'default' : 'secondary'}>{t.is_public ? 'Публичный' : 'Приватный'}</Badge>
            </div>
            <Button size="sm" variant="outline">Редактировать</Button>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
