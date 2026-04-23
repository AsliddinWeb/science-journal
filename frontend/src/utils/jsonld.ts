import type { Article } from '@/types/article'
import { normalizeKeywords } from '@/utils/truncate'

const SITE_URL = typeof window !== 'undefined' ? window.location.origin : ''

interface SiteBrand {
  siteName: string
  issn?: string
  logoUrl?: string
}

function publisher(brand: SiteBrand) {
  return {
    '@type': 'Organization',
    name: brand.siteName,
    url: SITE_URL,
    logo: {
      '@type': 'ImageObject',
      url: brand.logoUrl || `${SITE_URL}/favicon.svg`,
    },
  }
}

function isUploaderRole(role?: string): boolean {
  return role === 'superadmin'
}

export function buildScholarlyArticle(article: Article, brand: SiteBrand = { siteName: '' }): object {
  const titleEn = (article.title as any)?.en || (article.title as any)?.uz || ''
  const abstractEn = (article.abstract as any)?.en || (article.abstract as any)?.uz || ''

  const authors = []
  if (article.author && !isUploaderRole(article.author.role)) {
    authors.push({
      '@type': 'Person',
      name: article.author.full_name,
      ...(article.author.orcid_id ? { identifier: `https://orcid.org/${article.author.orcid_id}` } : {}),
      ...(article.author.affiliation ? { affiliation: { '@type': 'Organization', name: article.author.affiliation } } : {}),
    })
  }
  if (article.co_authors) {
    article.co_authors.forEach((ca: any) => {
      const name = ca.user ? ca.user.full_name : ca.guest_name
      if (!name) return
      const orcid = ca.user?.orcid_id || ca.guest_orcid
      const affiliation = ca.user?.affiliation || ca.guest_affiliation
      authors.push({
        '@type': 'Person',
        name,
        ...(orcid ? { identifier: `https://orcid.org/${orcid}` } : {}),
        ...(affiliation ? { affiliation: { '@type': 'Organization', name: affiliation } } : {}),
      })
    })
  }

  // Parse pages "82-86" -> pageStart / pageEnd
  let pageStart: string | undefined
  let pageEnd: string | undefined
  if (article.pages) {
    const m = article.pages.match(/^\s*(\d+)\s*[-–—]\s*(\d+)\s*$/)
    if (m) { pageStart = m[1]; pageEnd = m[2] }
  }

  return {
    '@context': 'https://schema.org',
    '@type': 'ScholarlyArticle',
    headline: titleEn,
    abstract: abstractEn,
    author: authors,
    datePublished: article.published_date,
    dateModified: article.updated_at,
    publisher: publisher(brand),
    ...(article.doi ? {
      identifier: { '@type': 'PropertyValue', propertyID: 'DOI', value: article.doi },
      sameAs: `https://doi.org/${article.doi}`,
    } : {}),
    inLanguage: article.language,
    isAccessibleForFree: true,
    license: 'https://creativecommons.org/licenses/by/4.0/',
    isPartOf: {
      '@type': article.issue ? 'PublicationIssue' : 'Periodical',
      ...(article.issue ? { issueNumber: article.issue.number } : {}),
      ...(article.volume ? {
        isPartOf: {
          '@type': 'PublicationVolume',
          volumeNumber: article.volume.number,
          isPartOf: {
            '@type': 'Periodical',
            name: brand.siteName,
            ...(brand.issn ? { issn: brand.issn } : {}),
          },
        },
      } : {
        name: brand.siteName,
        ...(brand.issn ? { issn: brand.issn } : {}),
      }),
    },
    ...(pageStart ? { pageStart } : {}),
    ...(pageEnd ? { pageEnd } : {}),
    ...(article.pages && !pageStart ? { pagination: article.pages } : {}),
    keywords: normalizeKeywords(article.keywords).join(', '),
    url: `${SITE_URL}/articles/${article.id}`,
    mainEntityOfPage: {
      '@type': 'WebPage',
      '@id': `${SITE_URL}/articles/${article.id}`,
    },
  }
}

export function buildWebSite(brand: SiteBrand = { siteName: '' }): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: brand.siteName,
    url: SITE_URL,
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: `${SITE_URL}/search?q={search_term_string}`,
      },
      'query-input': 'required name=search_term_string',
    },
  }
}

export function buildOrganization(brand: SiteBrand = { siteName: '' }): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: brand.siteName,
    url: SITE_URL,
    logo: {
      '@type': 'ImageObject',
      url: brand.logoUrl || `${SITE_URL}/favicon.svg`,
    },
    sameAs: [SITE_URL],
    publishingPrinciples: `${SITE_URL}/pages/peer-review`,
  }
}

export function buildBreadcrumb(items: { name: string; url: string }[]): object {
  return {
    '@context': 'https://schema.org',
    '@type': 'BreadcrumbList',
    itemListElement: items.map((item, i) => ({
      '@type': 'ListItem',
      position: i + 1,
      name: item.name,
      item: item.url.startsWith('http') ? item.url : `${SITE_URL}${item.url}`,
    })),
  }
}
