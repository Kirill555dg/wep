import { useState, useCallback, Suspense, lazy } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader } from '@/shared/ui/loader'
import { Button } from '@/shared/ui/button'
import { Maximize2, Minimize2, X } from 'lucide-react'

const TypstPreview = lazy(() => import('@/features/render/ui/TypstPreview'))

interface TypstRenderProps {
  source: string
  testId?: number | string
  questionId?: number | string
  mode?: 'take' | 'edit' | 'review'
  /** compact=true: auto page width, natural SVG size (for formulas inside option cards) */
  compact?: boolean
}

function FallbackContent({ source }: { source: string }) {
  return <div className="text-sm whitespace-pre-wrap">{source}</div>
}

function TypstContent({ source, failed, compact }: { source: string; failed: boolean; compact?: boolean }) {
  if (failed) return <FallbackContent source={source} />
  return (
    <Suspense fallback={<Loader />}>
      <TypstPreview source={source} compact={compact} />
    </Suspense>
  )
}

export default function TypstRender({ source, mode, compact }: TypstRenderProps) {
  const [fullscreen, setFullscreen] = useState(false)
  const toggleFullscreen = useCallback(() => setFullscreen(v => !v), [])

  if (!source) {
    return compact
      ? <span className="text-sm text-muted-foreground italic">—</span>
      : <div className="py-4 text-muted-foreground text-sm text-center">Текст вопроса не задан</div>
  }

  if (compact) {
    return <TypstContent source={source} failed={false} compact />
  }

  return (
    <>
      <div className="w-full relative group">
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <Button variant="secondary" size="icon" className="h-7 w-7 shadow-sm" onClick={toggleFullscreen} title="На весь экран">
            <Maximize2 className="h-3.5 w-3.5" />
          </Button>
        </div>
        <TypstContent source={source} failed={false} compact={false} />
      </div>

      <AnimatePresence>
        {fullscreen && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 md:p-8"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={toggleFullscreen}
          >
            <motion.div
              className="relative w-full max-w-4xl max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col"
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', duration: 0.4 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="flex items-center justify-between px-4 py-3 border-b shrink-0">
                <span className="text-sm font-semibold">Предпросмотр</span>
                <Button variant="ghost" size="icon" className="h-8 w-8" onClick={toggleFullscreen}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                <TypstContent source={source} failed={false} compact={false} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
