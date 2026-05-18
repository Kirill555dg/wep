/**
 * Error handler for API calls.
 * Extract { error: { code, message } } from backend responses.
 */
export function getApiError(err: unknown): { code: string; message: string } {
  const anyErr = err as Record<string, unknown>
  const body = anyErr?.error as Record<string, string> | undefined
  return {
    code: body?.code ?? 'unknown',
    message: body?.message ?? String(err),
  }
}
