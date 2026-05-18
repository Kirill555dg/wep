import { useState, useRef, ChangeEvent } from 'react'
import { Image, Music, Video, Plus, X, FileImage, Upload } from 'lucide-react'
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

const TYPE_ICONS = {
  image: <Image className="h-3.5 w-3.5" />,
  audio: <Music className="h-3.5 w-3.5" />,
  video: <Video className="h-3.5 w-3.5" />,
}

export default function MediaCarousel({ files, mode, onChange }: MediaCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()
  const isEdit = mode === 'edit'

  const active = files[Math.min(activeIndex, files.length - 1)] ?? null

  const handleRemove = (idx: number) => {
    const next = files.filter((_, i) => i !== idx)
    onChange?.(next)
    if (activeIndex >= next.length) setActiveIndex(Math.max(0, next.length - 1))
  }

  const upload = async (file: File) => {
    if (files.length >= 10) { toast.error('Максимум 10 файлов'); return }
    setUploading(true)
    try {
      const res = await uploadMediaApiV1MediaUploadPost({ body: { file: file as Blob } })
      const data = (res.data || res) as any
      const url: string = data?.url ?? data?.data?.url ?? ''
      if (!url) { toast.error('Ошибка загрузки'); return }
      const type: MediaFile['type'] = file.type.startsWith('audio/')
        ? 'audio' : file.type.startsWith('video/') ? 'video' : 'image'
      onChange?.([...files, { id: String(Date.now()), url, type, filename: file.name }])
      setActiveIndex(files.length)
    } catch {
      toast.error('Ошибка загрузки')
    } finally {
      setUploading(false)
    }
  }

  const handleChange = async (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) await upload(file)
    e.target.value = ''
  }

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files?.[0]
    if (file) await upload(file)
  }

  if (!files.length && !isEdit) return null

  return (
    <div className="space-y-3">
      {/* Thumbnails row */}
      {files.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {files.map((f, i) => (
            <button
              key={f.id}
              onClick={() => setActiveIndex(i)}
              className={`group relative flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                i === activeIndex
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background text-foreground border-border hover:border-primary/50'
              }`}
            >
              {TYPE_ICONS[f.type]}
              <span className="max-w-[80px] truncate">{f.filename}</span>
              {isEdit && (
                <span
                  role="button"
                  onClick={(e) => { e.stopPropagation(); handleRemove(i) }}
                  className="ml-0.5 opacity-0 group-hover:opacity-100 transition-opacity rounded-full hover:bg-black/20 p-0.5"
                >
                  <X className="h-3 w-3" />
                </span>
              )}
            </button>
          ))}

          {isEdit && files.length < 10 && (
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border border-dashed border-muted-foreground/40 text-muted-foreground hover:border-primary/50 hover:text-primary transition-all disabled:opacity-50"
            >
              <Plus className="h-3.5 w-3.5" />
              {uploading ? 'Загрузка...' : 'Добавить'}
            </button>
          )}
        </div>
      )}

      {/* Preview */}
      {active ? (
        <div className="rounded-xl border overflow-hidden bg-black/5">
          {active.type === 'image' && (
            <img
              src={active.url}
              alt={active.filename}
              className="max-h-[280px] w-full object-contain"
            />
          )}
          {active.type === 'audio' && (
            <div className="p-4 flex flex-col items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                <Music className="h-6 w-6 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground truncate max-w-full">{active.filename}</p>
              <audio controls src={active.url} className="w-full" />
            </div>
          )}
          {active.type === 'video' && (
            <video controls src={active.url} className="max-h-[280px] w-full" />
          )}
        </div>
      ) : isEdit && (
        <div
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`rounded-xl border-2 border-dashed p-8 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-primary bg-primary/5 scale-[1.01]'
              : 'border-muted-foreground/25 hover:border-primary/40 hover:bg-muted/40'
          }`}
        >
          <Upload className={`h-8 w-8 mx-auto mb-2 transition-colors ${dragOver ? 'text-primary' : 'text-muted-foreground'}`} />
          <p className="text-sm font-medium text-muted-foreground">
            {uploading ? 'Загрузка...' : 'Перетащите или кликните для добавления медиа'}
          </p>
          <p className="text-xs text-muted-foreground/70 mt-1">Изображения, аудио, видео — до 10 МБ</p>
        </div>
      )}

      {isEdit && (
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept="image/*,audio/*,video/*,application/pdf,.doc,.docx,.txt,.zip"
          onChange={handleChange}
        />
      )}
    </div>
  )
}
