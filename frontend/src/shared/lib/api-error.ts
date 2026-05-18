/**
 * Error handler for API calls.
 * Extract { error: { code, message } } from backend responses.
 */
export function getApiError(err: unknown): { code: string; message: string } {
  const anyErr = err as Record<string, unknown>
  const nestedError = anyErr?.error
  const body = (typeof nestedError === 'object' && nestedError !== null) 
    ? (nestedError as Record<string, unknown>).error as Record<string, string> | undefined
    : undefined
  
  const message = body?.message ?? 
                 anyErr?.message as string ?? 
                 (typeof anyErr === 'string' ? anyErr : 
                 'Произошла ошибка. Попробуйте снова.')
  
  return {
    code: body?.code ?? (typeof nestedError === 'object' ? (nestedError as Record<string, unknown>).code as string : undefined) ?? 'unknown',
    message: message,
  }
}
