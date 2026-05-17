import {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import {useCatalogSearch} from '@/features/catalog/api/useCatalog'
import {Button} from '@/shared/ui/button'
import {Card, CardContent, CardHeader, CardTitle} from '@/shared/ui/card'
import {Badge} from '@/shared/ui/badge'
import {Loader} from '@/shared/ui/loader'
import SearchBar from '@/widgets/search-bar/ui/SearchBar'

export default function CatalogPage() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const {data: tests, isLoading} = useCatalogSearch(q, tags)

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Каталог тестов</h1>
        <Button onClick={() => navigate('/editor')}>Создать тест</Button>
      </div>
      <SearchBar onSearch={(newQ, newTags) => { setQ(newQ); setTags(newTags) }} />
      {isLoading && <Loader />}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {(tests as any)?.data?.map((t: any) => (
          <Card key={t.id} className="cursor-pointer hover:shadow-md transition" onClick={() => navigate(`/take/${t.id}`)}>
            <CardHeader><CardTitle className="text-lg">{t.title}</CardTitle></CardHeader>
            <CardContent className="space-y-2">
              <p className="text-sm text-muted-foreground line-clamp-2">{t.description}</p>
              <div className="flex flex-wrap gap-1">{t.tags?.map((tag: any) => <Badge key={tag.id} variant="secondary">{tag.name}</Badge>)}</div>
              <p className="text-xs text-muted-foreground">Вопросов: {t.questions_count || 0}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
