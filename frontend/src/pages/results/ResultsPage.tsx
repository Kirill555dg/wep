import {useParams} from 'react-router-dom'
import {useAttemptResult} from '@/features/taking/api/useTaking'
import {Loader} from '@/shared/ui/loader'

export default function ResultsPage() {
  const {attemptId} = useParams()
  const {data, isLoading} = useAttemptResult(Number(attemptId))

  if (isLoading) return <Loader />

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-2">Результаты</h1>
      <p className="text-lg">Баллы: {data?.data?.score} / {data?.data?.max_score}</p>
    </div>
  )
}
