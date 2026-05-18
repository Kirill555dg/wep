import {useRef} from 'react'
import {Camera} from 'lucide-react'
import {Avatar, AvatarFallback, AvatarImage} from '@/shared/ui/avatar'

interface Props {
  initials: string
  previewUrl?: string
  onSelect: (file: File) => void
  disabled?: boolean
}

export function ProfileAvatarBlock({
  initials,
  previewUrl,
  onSelect,
  disabled,
}: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleClick = () => {
    if (!disabled) fileInputRef.current?.click()
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) onSelect(file)
  }

  return (
    <div className="flex flex-col items-center">
      <div className="relative cursor-pointer" onClick={handleClick}>
        <Avatar className="h-20 w-20">
          <AvatarImage src={previewUrl ?? ''} alt="avatar" />
          <AvatarFallback className="text-xl">{initials}</AvatarFallback>
        </Avatar>
        <div className="absolute bottom-0 right-0 bg-primary text-primary-foreground rounded-full p-1.5">
          <Camera className="h-4 w-4" />
        </div>
      </div>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleChange}
        disabled={disabled}
      />
    </div>
  )
}
