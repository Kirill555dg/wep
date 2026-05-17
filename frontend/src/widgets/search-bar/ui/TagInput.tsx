/**
 * Tag selector with create support.
 */
import {useState} from 'react'
import {useQuery} from '@tanstack/react-query'
import {listTagsApiV1TagsGet, createTagApiV1TagsPost} from '@/shared/api/client/tags'
import {Badge} from '@/shared/ui/badge'
import {Input} from '@/shared/ui/input'
import {Button} from '@/shared/ui/button'

interface TagInputProps {
  selected: string[]
  onChange: (tags: string[]) => void
}

export default function TagInput({selected, onChange}: TagInputProps) {
  const {data} = useQuery({queryKey: ['tags'], queryFn: () => listTagsApiV1TagsGet()})
  const [newTag, setNewTag] = useState('')

  const allTags = (data as any)?.data || []

  const addTag = (name: string) => {
    if (!selected.includes(name)) onChange([...selected, name])
  }

  const removeTag = (name: string) => {
    onChange(selected.filter(t => t !== name))
  }

  const handleCreate = async () => {
    if (!newTag.trim()) return
    await createTagApiV1TagsPost({name: newTag.trim()})
    addTag(newTag.trim())
    setNewTag('')
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1">
        {selected.map(tag => <Badge key={tag} variant="default" className="cursor-pointer" onClick={() => removeTag(tag)}>{tag} ×</Badge>)}
      </div>
      <div className="flex items-center gap-2">
        <Input value={newTag} onChange={e => setNewTag(e.target.value)} placeholder="Новый тег" />
        <Button size="sm" onClick={handleCreate}>Добавить</Button>
      </div>
      <div className="flex flex-wrap gap-1">
        {allTags.map((t: any) => (
          <Badge key={t.id} variant="outline" className="cursor-pointer" onClick={() => addTag(t.name)}>{t.name}</Badge>
        ))}
      </div>
    </div>
  )
}
