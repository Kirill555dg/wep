/**
 * Error handler for API calls.
 * Extract { error: { code, message } } from backend responses.
 */
export function getApiError(err: unknown): { code: string; message: string } {
  const anyErr = err as Record<string, unknown>
  const body = anyErr?.error as Record<string, string> | undefined
  const message = body?.message ?? 
                 (typeof anyErr === 'string' ? anyErr : 
                 anyErr?.message as string ?? JSON.stringify(err))
  
  return {
    code: body?.code ?? 'unknown',
    message: message,
  }
}
