import {useState} from 'react'
import {useCatalogSearch} from '@/features/catalog/api/useCatalog'
import {Input} from '@/shared/ui/input'
import {Button} from '@/shared/ui/button'
import TagInput from './TagInput'

export default function SearchBar() {
  const [q, setQ] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const {refetch} = useCatalogSearch(q, tags)

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <Input placeholder="Поиск по названию..." value={q} onChange={e => setQ(e.target.value)} />
        <Button onClick={() => refetch()}>Найти</Button>
      </div>
      <TagInput selected={tags} onChange={setTags} />
    </div>
  )
}
