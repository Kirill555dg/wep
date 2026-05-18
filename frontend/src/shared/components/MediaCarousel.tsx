/**
 * MediaCarousel — media chips + preview for a question.
 *
 * Supports image/audio/video. Edit mode offers add/remove.
 */
import { useState, useRef, ChangeEvent } from 'react'
import { Image, Music, Video, Plus, X } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Badge } from '@/shared/ui/badge'
import { uploadMediaApiV1MediaUploadPost } from '@/shared/api'
import { useToast } from '@/shared/hooks/useToast'

export interface MediaFile {
  id: string
  url: string
  type: 'image' | 'audio' | 'video'
  filename: string
}

interface MediaCarouselProps {
  files: MediaFile[]
  mode: 'take' | 'edit' | 'review'
  onChange?: (files: MediaFile[]) => void
}

export default function MediaCarousel({ files, mode, onChange }: MediaCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  const isEdit = mode === 'edit'

  const active = files[activeIndex] || null

  const handleRemove = (idx: number) => {
    const next = files.filter((_, i) => i !== idx)
    onChange?.(next)
    if (activeIndex >= next.length) {
      setActiveIndex(Math.max(0, next.length - 1))
    }
  }

  const handleAdd = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (files.length >= 10) {
      toast.error('Max 10 media files')
      e.target.value = ''
      return
    }
    setUploading(true)
    try {
      const res = await uploadMediaApiV1MediaUploadPost({
        body: { file: file as Blob },
      })
      const data = (res.data || res) as any
      const url: string = data?.url ?? data?.data?.url ?? ''
      if (url) {
        const type: MediaFile['type'] = file.type.startsWith('audio/')
          ? 'audio'
          : file.type.startsWith('video/')
            ? 'video'
            : 'image'
        const next: MediaFile = {
          id: String(Date.now()),
          url,
          type,
          filename: file.name,
        }
        onChange?.([...files, next])
      } else {
        toast.error('Upload failed: no URL returned')
      }
    } catch (err) {
      toast.error('Upload failed')
    } finally {
      setUploading(false)
      e.target.value = ''
    }
  }

  const iconFor = (t: MediaFile['type']) => {
    if (t === 'image') return <Image className="h-3 w-3 mr-1" />
    if (t === 'audio') return <Music className="h-3 w-3 mr-1" />
    return <Video className="h-3 w-3 mr-1" />
  }

  if (!files.length && !isEdit) return null

  return (
    <div className="w-full my-4">
      <div className="flex flex-wrap items-center gap-2 mb-3">
        {files.map((f, i) => (
          <Badge
            key={f.id}
            variant={i === activeIndex ? 'default' : 'outline'}
            className="cursor-pointer select-none gap-1"
            onClick={() => setActiveIndex(i)}
          >
            {iconFor(f.type)}
            {i + 1}/{files.length}
            {isEdit && (
              <button
                className="ml-1 rounded-sm hover:bg-destructive/20"
                onClick={(e) => {
                  e.stopPropagation()
                  handleRemove(i)
                }}
              >
                <X className="h-3 w-3" />
              </button>
            )}
          </Badge>
        ))}
        {isEdit && files.length < 10 && (
          <Button
            variant="ghost"
            size="sm"
            disabled={uploading}
            onClick={() => fileInputRef.current?.click()}
          >
            <Plus className="h-3 w-3 mr-1" />
            Add Media
          </Button>
        )}
      </div>

      {active ? (
        <div className="rounded-lg border bg-gray-50 p-2 flex items-center justify-center min-h-[200px]">
          {active.type === 'image' && (
            <img
              src={active.url}
              alt={active.filename}
              className="max-h-[300px] w-auto object-contain"
            />
          )}
          {active.type === 'audio' && (
            <audio controls src={active.url} className="w-full" />
          )}
          {active.type === 'video' && (
            <video controls src={active.url} className="max-h-[300px] w-full" />
          )}
        </div>
      ) : isEdit ? (
        <div
          className="rounded-lg border-2 border-dashed border-muted-foreground/25 p-6 text-center cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <p className="text-sm text-muted-foreground">
            Drag & drop or click to add media
          </p>
        </div>
      ) : null}

      {isEdit && (
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept="image/*,audio/*,video/*"
          onChange={handleAdd}
        />
      )}
    </div>
  )
}
