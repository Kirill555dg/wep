/**
 * TypstEditorPage — live Typst editing sub-page.
 *
 * Split layout: raw source textarea on the left, live preview on the right.
 * Debounced preview. Save & Close patches the question text.
 */
import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/shared/ui/button'
import { Textarea } from '@/shared/ui/textarea'
import TypstRender from '@/shared/components/TypstRender'
import { updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch } from '@/shared/api'
import { useToast } from '@/shared/hooks/useToast'

export default function TypstEditorPage() {
  const { testId, questionId } = useParams()
  const navigate = useNavigate()
  const toast = useToast()

  const [source, setSource] = useState('')
  const [debouncedSource, setDebouncedSource] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSource(source), 500)
    return () => clearTimeout(timer)
  }, [source])

  const handleSave = useCallback(async () {
    if (!testId || !questionId) return
    setSaving(true)
    try {
      await updateQuestionApiV1TestsTestIdQuestionsQuestionIdPatch({
        path: { test_id: Number(testId), question_id: Number(questionId) },
        body: { text: source },
      })
      toast.success('Saved')
      navigate(`/tests/${testId}/edit`)
    } catch (err) {
      toast.error('Save failed')
    } finally {
      setSaving(false)
    }
  }, [testId, questionId, source, navigate, toast])

  return (
    <div className="h-screen flex flex-col">
      <div className="flex items-center justify-between px-4 py-3 border-b">
        <Button variant="ghost" size="sm" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <h1 className="text-sm font-semibold">Typst Editor</h1>
        <Button size="sm" disabled={saving} onClick={handleSave}>
          Save & Close
        </Button>
      </div>
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        <div className="flex-1 p-4 flex flex-col min-h-0">
          <label className="text-xs font-medium text-muted-foreground mb-1">Source</label>
          <Textarea
            className="flex-1 resize-none font-mono text-sm"
            value={source}
            onChange={(e) => setSource(e.target.value)}
            placeholder="Type your Typst source here..."
          />
        </div>
        <div className="flex-1 p-4 flex flex-col min-h-0 border-t md:border-t-0 md:border-l">
          <label className="text-xs font-medium text-muted-foreground mb-1">Preview</label>
          <div className="flex-1 overflow-auto border rounded-lg p-2 bg-background">
            <TypstRender source={debouncedSource} />
          </div>
        </div>
      </div>
    </div>
  )
}
