export function formatScore(score: number, max: number): string {
  const pct = max > 0 ? Math.round((score / max) * 100) : 0;
  return `${score} / ${max} (${pct}%)`;
}
