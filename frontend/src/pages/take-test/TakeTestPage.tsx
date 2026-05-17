import {useParams} from 'react-router-dom'
import {useTestDetail} from '@/features/test-management/api/useTests'
import {Button} from '@/shared/ui/button'
import {Loader} from '@/shared/ui/loader'

export default function TakeTestPage() {
  const {testId} = useParams()
  const {data: test, isLoading} = useTestDetail(Number(testId))

  if (isLoading) return <Loader />

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">{test?.data?.title || 'Тест'}</h1>
      <p className="text-muted-foreground">{test?.data?.description}</p>
      <Button>Начать прохождение</Button>
    </div>
  )
}
