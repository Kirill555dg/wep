/**
 * TypstRender — wrapper for Typst source rendering.
 *
 * Lazy-loads the real Typst WASM renderer.
 * Falls back to plain text if source contains math delimiters or if WASM fails.
 */
import { useState, Suspense, lazy } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader } from '@/shared/ui/loader'
import { Button } from '@/shared/ui/button'
import { Pencil } from 'lucide-react'

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
      <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">{source}</pre>
    )
  }
  return (
    <div className="prose max-w-none whitespace-pre-wrap">{source}</div>
  )
}

export default function TypstRender({ source, testId, questionId, mode }: TypstRenderProps) {
  const [failed, setFailed] = useState(false)
  const navigate = useNavigate()

  if (!source) {
    return (
      <div className="w-full min-h-[200px] flex items-center justify-center text-muted-foreground">
        Empty question text
      </div>
    )
  }

  const hasMath = source.includes('$')

  if (hasMath || failed) {
    return (
      <div className="w-full max-h-[50vh] overflow-y-auto">
        <FallbackRender source={source} />
        {mode === 'edit' && testId && questionId && (
          <Button
            variant="ghost"
            size="sm"
            className="mt-2"
            onClick={() => navigate(`/tests/${testId}/questions/${questionId}/typst`)}
          >
            <Pencil className="h-4 w-4 mr-1" />
            Edit
          </Button>
        )}
      </div>
    )
  }

  return (
    <div className="w-full max-h-[50vh] overflow-y-auto min-h-[200px]">
      <Suspense fallback={<Loader />}>
        <TypstPreview source={source} />
      </Suspense>
      {mode === 'edit' && testId && questionId && (
        <Button
          variant="ghost"
          size="sm"
          className="mt-2"
          onClick={() => navigate(`/tests/${testId}/questions/${questionId}/typst`)}
        >
          <Pencil className="h-4 w-4 mr-1" />
          Edit
        </Button>
      )}
    </div>
  )
}
