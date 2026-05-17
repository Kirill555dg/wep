import React, {Suspense, useEffect, useState} from 'react';
import {Loader} from '@/shared/ui/loader';

interface TypstPreviewProps {
  source: string;
  className?: string;
}

const moduleName = '@myriaddreamin/typst.ts';

function TypstInner({source, className}: TypstPreviewProps) {
  const [html, setHtml] = useState<string>('');
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function compile() {
      try {
        const mod = await import(/* @vite-ignore */ moduleName);
        const compiler = (mod as Record<string, unknown>).createTypst ?? (mod as Record<string, unknown>).compiler ?? (mod as Record<string, unknown>).default;
        if (typeof compiler === 'function') {
          const result = await (compiler as (...args: unknown[]) => Promise<string>)({mainContent: source});
          if (!cancelled) setHtml(result);
          return;
        }
        if (typeof (mod as Record<string, unknown>).render === 'function') {
          const result = await ((mod as Record<string, unknown>).render as (...args: unknown[]) => Promise<string>)(source);
          if (!cancelled) setHtml(result);
          return;
        }
        setError(true);
      } catch {
        setError(true);
      }
    }

    compile();
    return () => { cancelled = true; };
  }, [source]);

  if (error) {
    return (
      <div className={className}>
        <pre className="bg-muted p-4 rounded-md overflow-auto text-sm whitespace-pre-wrap">{source}</pre>
      </div>
    );
  }

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{__html: html || `<div class="text-muted-foreground">Compiling...</div>`}}
    />
  );
}

export default function TypstPreview(props: TypstPreviewProps) {
  return (
    <Suspense fallback={<Loader />}>
      <TypstInner {...props} />
    </Suspense>
  );
}
