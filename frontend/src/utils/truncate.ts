export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength).trimEnd() + '…'
}

export function getLocalizedField(
  obj: Record<string, string> | undefined | null,
  locale: string,
  fallback: string = ''
): string {
  if (!obj) return fallback
  return obj[locale] || obj['en'] || obj['uz'] || obj['ru'] || fallback
}
