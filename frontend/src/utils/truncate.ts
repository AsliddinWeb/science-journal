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

/**
 * Normalize multilingual-or-flat list (keywords / references) into a string[].
 * Accepts either string[] or { uz?: [], ru?: [], en?: [] }.
 */
export function normalizeMultilingualList(
  value: string[] | { uz?: string[]; ru?: string[]; en?: string[] } | null | undefined,
  locale?: string,
): string[] {
  if (!value) return []
  if (Array.isArray(value)) return value.filter(Boolean)
  const dict = value as { uz?: string[]; ru?: string[]; en?: string[] }
  if (locale && Array.isArray(dict[locale as 'uz' | 'ru' | 'en']) && dict[locale as 'uz' | 'ru' | 'en']!.length) {
    return dict[locale as 'uz' | 'ru' | 'en']!.filter(Boolean)
  }
  // Fallback: concat all languages, dedupe
  const all = [...(dict.uz ?? []), ...(dict.ru ?? []), ...(dict.en ?? [])].filter(Boolean)
  return Array.from(new Set(all))
}

/** @deprecated use normalizeMultilingualList */
export const normalizeKeywords = normalizeMultilingualList
