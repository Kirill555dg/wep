/**
 * Initialize and cache a global typst.ts compiler/renderer.
 *
 * The snippet `$typst` handles fetch of WASM and fonts automatically.
 */
import * as typstSnippet from '@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs';

let ready = false;

export async function initTypst(): Promise<void> {
  if (ready) return;
  // Dynamically import so Vite can chunk it.
  const {$typst} = await import('@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs');
  // Warm-up with empty compile to fetch WASM.
  await $typst.svg({mainContent: ''});
  ready = true;
}

export async function renderTypstSvg(source: string): Promise<string> {
  if (!ready) await initTypst();
  const {$typst} = await import('@myriaddreamin/typst.ts/dist/esm/contrib/snippet.mjs');
  return $typst.svg({mainContent: source});
}
