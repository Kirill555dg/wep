interface TypstEditorProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
  height?: string
}

import {useEffect} from 'react'
import {TypstPreview} from '@/features/render/ui/TypstPreview'
import {debounce} from '@/shared/lib/utils'

export default function TypstEditor({
  value,
  onChange,
  placeholder = 'Введите Typst разметку...',
  className = '',
  height = '400px',
}: TypstEditorProps) {
  const debouncedOnChange = debounce(onChange, 300)

  useEffect(() => {
    return () => {
      debouncedOnChange.cancel?.()
    }
  }, [debouncedOnChange])

  return (
    <div className={`flex h-full ${className}`}>
      <div className="flex w-1/2 flex-col border-r border-neutral-200">
        <div className="flex items-center border-b border-neutral-200 bg-neutral-50 px-4 py-2">
          <span className="text-sm font-medium text-neutral-700">
            Редактирование
          </span>
          <span className="ml-auto text-xs text-neutral-500">
            Typst разметка
          </span>
        </div>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="h-full w-full resize-none bg-neutral-50 p-4 font-mono text-sm focus:outline-none"
          style={{height}}
          spellCheck={false}
        />
      </div>
      <div className="flex w-1/2 flex-col">
        <div className="flex items-center border-b border-neutral-200 bg-neutral-50 px-4 py-2">
          <span className="text-sm font-medium text-neutral-700">
            Предпросмотр
          </span>
          <span className="ml-auto text-xs text-neutral-500">
            Отрисовка
          </span>
        </div>
        <div className="flex-1 overflow-auto p-4">
          <TypstPreview 
            source={value} 
            className="min-h-full min-w-full"
          />
        </div>
      </div>
    </div>
  )
}
