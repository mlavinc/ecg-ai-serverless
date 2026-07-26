export function formatPercent(value: number, digits = 1): string {
  return `${(value * 100).toFixed(digits)}%`
}

export function formatMs(value: number): string {
  if (value < 1) return '<1 ms'
  return `${value.toFixed(value < 10 ? 1 : 0)} ms`
}

export function formatFeatureName(key: string): string {
  return key
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ')
}

export function titleCase(value: string): string {
  return value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}
