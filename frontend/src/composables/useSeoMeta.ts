import { watch } from 'vue'
import { useRoute } from 'vue-router'

const SITE_NAME = 'Science and Innovation Journal'
const DEFAULT_DESCRIPTION =
  "International scientific journal covering science, technology and innovation. Open access, peer-reviewed. ISSN 2181-3337"
const DEFAULT_OG_IMAGE = '/og-default.png'
const SITE_URL = 'https://scientists.uz'

export interface SeoOptions {
  title?: string
  description?: string
  keywords?: string
  ogTitle?: string
  ogDescription?: string
  ogImage?: string
  ogUrl?: string
  canonical?: string
  type?: 'website' | 'article'
}

export interface CitationMeta {
  title: string
  authors: string[] // array of "Last, First" or "Full Name"
  publicationDate?: string // ISO date
  journalTitle?: string
  issn?: string
  volume?: string | number
  issue?: string | number
  firstpage?: string | number
  lastpage?: string | number
  pdfUrl?: string
  doi?: string
  abstractHtmlUrl?: string
  language?: string
  keywords?: string[]
  publisher?: string
}

function removeMetaByName(name: string) {
  document.querySelectorAll(`meta[name="${name}"]`).forEach(el => el.remove())
}

/** Set multiple meta tags with the same name (for citation_author etc.) */
function setMetaMultiple(name: string, values: string[]) {
  removeMetaByName(name)
  values.forEach(value => {
    if (!value) return
    const el = document.createElement('meta')
    el.setAttribute('name', name)
    el.setAttribute('content', value)
    document.head.appendChild(el)
  })
}

/** Apply Google Scholar citation_* meta tags. Call when article data is loaded. */
export function applyCitationMeta(m: CitationMeta) {
  // Remove all previous citation_* tags first
  document.querySelectorAll('meta[name^="citation_"]').forEach(el => el.remove())

  if (m.title) setMeta('citation_title', m.title, true)
  if (m.authors && m.authors.length) setMetaMultiple('citation_author', m.authors)
  if (m.publicationDate) {
    // Convert to YYYY/MM/DD format
    try {
      const d = new Date(m.publicationDate)
      const formatted = `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getDate()).padStart(2, '0')}`
      setMeta('citation_publication_date', formatted, true)
      setMeta('citation_online_date', formatted, true)
    } catch { /* ignore */ }
  }
  if (m.journalTitle) setMeta('citation_journal_title', m.journalTitle, true)
  if (m.issn) setMeta('citation_issn', m.issn, true)
  if (m.volume) setMeta('citation_volume', String(m.volume), true)
  if (m.issue) setMeta('citation_issue', String(m.issue), true)
  if (m.firstpage) setMeta('citation_firstpage', String(m.firstpage), true)
  if (m.lastpage) setMeta('citation_lastpage', String(m.lastpage), true)
  if (m.pdfUrl) setMeta('citation_pdf_url', m.pdfUrl.startsWith('http') ? m.pdfUrl : `${SITE_URL}${m.pdfUrl}`, true)
  if (m.doi) setMeta('citation_doi', m.doi, true)
  if (m.abstractHtmlUrl) setMeta('citation_abstract_html_url', m.abstractHtmlUrl.startsWith('http') ? m.abstractHtmlUrl : `${SITE_URL}${m.abstractHtmlUrl}`, true)
  if (m.language) setMeta('citation_language', m.language, true)
  if (m.keywords && m.keywords.length) setMeta('citation_keywords', m.keywords.join('; '), true)
  if (m.publisher) setMeta('citation_publisher', m.publisher, true)
}

function setMeta(property: string, content: string, isName = false) {
  const attr = isName ? 'name' : 'property'
  let el = document.querySelector<HTMLMetaElement>(`meta[${attr}="${property}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, property)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function setLink(rel: string, href: string) {
  let el = document.querySelector<HTMLLinkElement>(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

export function useSeoMeta(options: SeoOptions = {}) {
  const route = useRoute()

  function apply(opts: SeoOptions) {
    const title = opts.title ? `${opts.title} | ${SITE_NAME}` : SITE_NAME
    const description = opts.description || DEFAULT_DESCRIPTION
    const ogTitle = opts.ogTitle || opts.title || SITE_NAME
    const ogDescription = opts.ogDescription || description
    const ogImage = opts.ogImage || DEFAULT_OG_IMAGE
    const ogUrl = opts.ogUrl || `${SITE_URL}${route.fullPath}`
    const canonical = opts.canonical || ogUrl

    document.title = title

    setMeta('description', description, true)
    if (opts.keywords) setMeta('keywords', opts.keywords, true)
    setMeta('robots', 'index, follow', true)

    // Open Graph
    setMeta('og:type', opts.type || 'website')
    setMeta('og:site_name', SITE_NAME)
    setMeta('og:title', ogTitle)
    setMeta('og:description', ogDescription)
    setMeta('og:image', ogImage.startsWith('http') ? ogImage : `${SITE_URL}${ogImage}`)
    setMeta('og:url', ogUrl)

    // Twitter Card
    setMeta('twitter:card', 'summary_large_image', true)
    setMeta('twitter:title', ogTitle, true)
    setMeta('twitter:description', ogDescription, true)
    setMeta('twitter:image', ogImage.startsWith('http') ? ogImage : `${SITE_URL}${ogImage}`, true)

    // Canonical
    setLink('canonical', canonical)
  }

  apply(options)

  // Reapply on route change for reactive usage
  watch(() => route.fullPath, () => apply(options))

  return { apply }
}
