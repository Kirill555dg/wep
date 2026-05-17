/**
 * Fallback Typst renderer — will be replaced with WASM once build issues resolved.
 */
export async function initTypst(): Promise<void> {}

export async function renderTypstSvg(source: string): Promise<string> {
  // Markdown-like simple formatting fallback until WASM build works.
  const html = source
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\$(.+?)\$/g, '<code>$1</code>')
    .replace(/\n/g, '<br/>')
  return `<div class="prose max-w-none">${html}</div>`
}
