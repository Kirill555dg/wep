import {$typst} from '@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs'

import compilerWasmUrl from '@myriaddreamin/typst-ts-web-compiler/pkg/typst_ts_web_compiler_bg.wasm?url'
import rendererWasmUrl from '@myriaddreamin/typst-ts-renderer/pkg/typst_ts_renderer_bg.wasm?url'

let configured = false

function ensureConfig(): void {
  if (configured) return
  configured = true
  $typst.setCompilerInitOptions({ getModule: () => compilerWasmUrl })
  $typst.setRendererInitOptions({ getModule: () => rendererWasmUrl })
}

// Full: fixed 480pt page → text wraps at reading width, scaled to fill container
const PREAMBLE_FULL = '#set text(size: 11pt)\n#set page(width: 480pt, height: auto, margin: 5pt)\n'

// Compact: auto page → SVG keeps natural formula size
const PREAMBLE_COMPACT = '#set text(size: 16pt)\n#set page(width: auto, height: auto, margin: 5pt)\n'

export async function renderTypstSvg(source: string, compact = false): Promise<string> {
  ensureConfig()
  const preamble = compact ? PREAMBLE_COMPACT : PREAMBLE_FULL
  let html = await $typst.svg({mainContent: preamble + source})

  if (compact) {
    // Keep SVG's natural width/height attributes so it displays at natural size.
    // Only add max-width to prevent overflow.
    return html.replace('<svg ', '<svg style="max-width:100%;height:auto;display:block" ')
  } else {
    // Full mode: strip fixed dimensions, force 100% width so content fills the container.
    html = html
      .replace(/(<svg[^>]*?)\s+width="[^"]*"/, '$1')
      .replace(/(<svg[^>]*?)\s+height="[^"]*"/, '$1')
    return html.replace('<svg ', '<svg style="width:100%;height:auto;display:block" ')
  }
}
