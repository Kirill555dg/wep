import {useEffect, useRef, useState, Suspense} from 'react'
import {Loader} from '@/shared/ui/loader'
import {renderTypstSvg} from '@/shared/lib/typst'

interface TypstPreviewProps {
  source: string
  compact?: boolean
  className?: string
}

function _TypstPreview({source, compact, className}: TypstPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    renderTypstSvg(source, compact).then((html) => {
      if (!cancelled) setSvg(html)
    }).catch(() => {
      if (!cancelled) setSvg(`<pre style="font-size:13px;white-space:pre-wrap">${source}</pre>`)
    })
    return () => { cancelled = true }
  }, [source, compact])

  return (
    <div
      ref={containerRef}
      className={className ?? ''}
      dangerouslySetInnerHTML={{__html: svg}}
    />
  )
}

export default function TypstPreview(props: TypstPreviewProps) {
  return (
    <Suspense fallback={<Loader />}>
      <_TypstPreview {...props} />
    </Suspense>
  )
}
