/**
 * Media upload feature using presigned URL or direct upload to API.
 */
import {ChangeEvent, useState} from 'react'
import {uploadMediaApiV1MediaUploadPost} from '@/shared/api/client/media'
import {Button} from '@/shared/ui/button'
import {Input} from '@/shared/ui/input'
import {Loader} from '@/shared/ui/loader'

interface MediaUploadProps {
  onUploaded: (url: string) => void
}

export default function MediaUpload({onUploaded}: MediaUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    try {
      const payload = new FormData()
      payload.append('file', file)
      const res = await uploadMediaApiV1MediaUploadPost(payload as any)
      const url = (res as any).data?.url || (res as any).url
      if (url) onUploaded(url)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
      setFile(null)
    }
  }

  return (
    <div className="flex items-center gap-2">
      <Input type="file" accept="image/jpeg,image/png,image/gif,image/webp" onChange={(e: ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)} />
      <Button size="sm" disabled={!file || loading} onClick={handleUpload}>{loading ? <Loader /> : 'Загрузить'}</Button>
    </div>
  )
}
