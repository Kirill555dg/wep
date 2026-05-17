/**
 * Full attempt results page with per-question review.
 */
import {useParams} from 'react-router-dom'
import {useAttemptResult} from '@/features/taking/api/useTaking'
import TypstPreview from '@/features/render/ui/TypstPreview'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
import {Badge} from '@/shared/ui/badge'
import {Button} from '@/shared/ui/button'
import {Loader} from '@/shared/ui/loader'

export default function ResultsPage() {
  const {attemptId} = useParams()
  const {data, isLoading} = useAttemptResult(Number(attemptId))

  if (isLoading) return <Loader />
  const result = (data as any)?.data

  const percent = result?.max_score ? Math.round((result.score / result.max_score) * 100) : 0

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Результаты: {result?.test_title}</h1>
      <Card>
        <CardContent className="p-6 flex items-center justify-between">
          <div>
            <p className="text-3xl font-bold">{result?.score} / {result?.max_score}</p>
            <p className="text-muted-foreground">{percent}%</p>
          </div>
          <Badge variant={percent >= 60 ? 'default' : 'destructive'}>{percent >= 60 ? 'Зачтено' : 'Не зачтено'}</Badge>
        </CardContent>
      </Card>

      <div className="space-y-4">
        {result?.answers?.map((a: any, idx: number) => (
          <Card key={idx} className={a.is_correct ? 'border-green-300' : 'border-red-300'}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">Вопрос {idx + 1}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <TypstPreview source={a.question_text} className="text-sm" />
              {a.is_correct === null ? (
                <Badge variant="outline">На проверке</Badge>
              ) : a.is_correct ? (
                <Badge className="bg-green-100 text-green-800">Верно</Badge>
              ) : (
                <Badge className="bg-red-100 text-red-800">Неверно</Badge>
              )}
              {a.explanation && (
                <div className="text-sm text-muted-foreground bg-gray-50 rounded p-2">
                  <p className="font-medium">Объяснение:</p>
                  <TypstPreview source={a.explanation} />
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <Button onClick={() => navigator.clipboard.writeText(window.location.href)}>Копировать ссылку</Button>
    </div>
  )
}
