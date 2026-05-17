/**
 * Lazy-initializing component that renders Typst source as inline SVG.
 *
 * Uses @myriaddreamin/typst.ts WASM compiler.
 */
import {useEffect, useRef, useState, Suspense} from 'react'
import {Loader} from '@/shared/ui/loader'
import {renderTypstSvg} from '@/shared/lib/typst'

interface TypstPreviewProps {
  source: string
  className?: string
}

function _TypstPreview({source, className}: TypstPreviewProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')

  useEffect(() => {
    let cancelled = false
    renderTypstSvg(source).then((html) => {
      if (!cancelled) setSvg(html)
    }).catch(() => {
      if (!cancelled) setSvg(`<pre class="text-red-500">Typst render failed</pre>`)
    })
    return () => { cancelled = true }
  }, [source])

  return (
    <div ref={containerRef} className={className} dangerouslySetInnerHTML={{__html: svg}} />
  )
}

export default function TypstPreview(props: TypstPreviewProps) {
  return (
    <Suspense fallback={<Loader />}>
      <_TypstPreview {...props} />
    </Suspense>
  )
}
