/**
 * Self-hosted Typst renderer using @myriaddreamin/typst.ts.
 *
 * WASM modules are imported via Vite's ?url suffix — Vite copies them
 * to the output directory and provides an absolute URL at runtime.
 */
import {$typst} from '@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs'

import compilerWasmUrl from '@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm?url'
import rendererWasmUrl from '@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm?url'

let configured = false

function ensureConfig(): void {
  if (configured) return
  configured = true
  $typst.setCompilerInitOptions({
    getModule: () => compilerWasmUrl,
  })
  $typst.setRendererInitOptions({
    getModule: () => rendererWasmUrl,
  })
}

export async function renderTypstSvg(source: string): Promise<string> {
  ensureConfig()
  return $typst.svg({mainContent: source})
}
