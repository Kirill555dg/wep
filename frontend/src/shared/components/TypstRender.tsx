import { useState, useCallback, Suspense, lazy } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Loader } from '@/shared/ui/loader'
import { Button } from '@/shared/ui/button'
import { Pencil, Maximize2, Minimize2, X } from 'lucide-react'

const TypstPreview = lazy(() => import('@/features/render/ui/TypstPreview'))

interface TypstRenderProps {
  source: string
  testId?: number | string
  questionId?: number | string
  mode?: 'take' | 'edit' | 'review'
}

function FallbackRender({ source }: { source: string }) {
  const hasMath = source.includes('$')
  if (hasMath) {
    return (
      <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto whitespace-pre-wrap">{source}</pre>
    )
  }
  return (
    <div className="prose max-w-none whitespace-pre-wrap">{source}</div>
  )
}

function TypstContent({ source, failed }: { source: string; failed: boolean }) {
  if (failed) {
    const hasMath = source.includes('$')
    if (hasMath) {
      return <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto whitespace-pre-wrap">{source}</pre>
    }
    return <div className="prose max-w-none whitespace-pre-wrap">{source}</div>
  }

  return (
    <Suspense fallback={<Loader />}>
      <TypstPreview source={source} />
    </Suspense>
  )
}

export default function TypstRender({ source, testId, questionId, mode }: TypstRenderProps) {
  const [failed, setFailed] = useState(false)
  const [fullscreen, setFullscreen] = useState(false)
  const navigate = useNavigate()

  const toggleFullscreen = useCallback(() => {
    setFullscreen((prev) => !prev)
  }, [])

  if (!source) {
    return (
      <div className="w-full min-h-[200px] flex items-center justify-center text-muted-foreground">
        Empty question text
      </div>
    )
  }

  const editButton = mode === 'edit' && testId && questionId && (
    <Button
      variant="ghost"
      size="sm"
      onClick={() => navigate(`/tests/${testId}/questions/${questionId}/typst`)}
    >
      <Pencil className="h-4 w-4 mr-1" />
      Edit
    </Button>
  )

  return (
    <>
      <div className="w-full max-h-[50vh] overflow-y-auto min-h-[200px] relative group">
        <div className="sticky top-2 right-2 flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
          <Button
            variant="secondary"
            size="icon"
            className="h-8 w-8 shadow-sm"
            onClick={toggleFullscreen}
            title="Fullscreen"
          >
            <Maximize2 className="h-4 w-4" />
          </Button>
        </div>
        <TypstContent source={source} failed={failed} />
        {editButton}
      </div>

      <AnimatePresence>
        {fullscreen && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 md:p-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleFullscreen}
          >
            <motion.div
              className="relative w-full max-w-5xl max-h-[90vh] bg-white rounded-xl shadow-2xl overflow-hidden flex flex-col"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              transition={{ type: 'spring', duration: 0.4 }}
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between px-4 py-3 border-b shrink-0">
                <span className="text-sm font-semibold">Fullscreen</span>
                <div className="flex items-center gap-1">
                  {editButton}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={toggleFullscreen}
                  >
                    <Minimize2 className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={toggleFullscreen}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto p-6">
                <TypstContent source={source} failed={failed} />
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
