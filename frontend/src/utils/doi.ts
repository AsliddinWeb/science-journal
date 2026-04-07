export function formatDoiUrl(doi: string): string {
  const clean = doi.replace(/^https?:\/\/(dx\.)?doi\.org\//, '')
  return `https://doi.org/${clean}`
}

export function formatDoiDisplay(doi: string): string {
  return doi.replace(/^https?:\/\/(dx\.)?doi\.org\//, '')
}
