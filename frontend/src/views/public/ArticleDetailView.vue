<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Download, Share2, Copy, Check, Eye, ChevronRight, FileText,
  BookOpen, Tag, Calendar, Globe, Hash, AlertCircle, RefreshCw,
  BadgeCheck, Send, Users,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField, normalizeKeywords } from '@/utils/truncate'
import { formatDate } from '@/utils/formatDate'
import type { Article, ArticleAuthor, PaginatedResponse } from '@/types/article'
import type { UserPublic } from '@/types/user'
import ArticleAbstract from '@/components/article/ArticleAbstract.vue'
import ArticleCard from '@/components/article/ArticleCard.vue'
import PdfPreview from '@/components/ui/PdfPreview.vue'
import { useSeoMeta, applyCitationMeta } from '@/composables/useSeoMeta'
import { useJsonLd } from '@/composables/useJsonLd'
import { buildScholarlyArticle, buildBreadcrumb } from '@/utils/jsonld'
import { useSiteInfoStore } from '@/stores/siteInfo'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()
const siteInfo = useSiteInfoStore()

interface HomeSettingsData {
  hero_title: Record<string, string>
  issn_online: string | null
  issn_print: string | null
}

const article = ref<Article | null>(null)
const related = ref<Article[]>([])
const loading = ref(true)
const error = ref(false)
const copied = ref(false)
const citationCopied = ref(false)
const showPdfPreview = ref(false)
const homeSettings = ref<HomeSettingsData | null>(null)

const { apply: applySeo } = useSeoMeta()
const { inject: injectLd } = useJsonLd()

// Only superadmin (system/root) gets filtered out. Editors/reviewers can be real authors.
function isSystemAccount(role?: string): boolean {
  return role === 'superadmin'
}

// Uzbek patronymic suffixes — not surnames, must be preserved separately.
// The apostrophe class covers all common variants used in Uzbek Latin:
//   ' (ASCII \x27), ` (\x60), ´ (\xB4), ʻ (ʻ — official Uzbek),
//   ʼ (ʼ), ‘ (‘), ’ (’).
const UZ_AP = '[\\u02BB\\u02BC\\u2018\\u2019\\x27\\x60\\xB4]'
const UZ_PATRONYMIC = new RegExp(
  `^(o${UZ_AP}?g${UZ_AP}?li|og${UZ_AP}?li|ogli|qizi|qız[ıi])$`,
  'i',
)

/**
 * Format an author's full name in "Familiya, I. F." style for
 * citations and Google Scholar's citation_author tag. Handles:
 *   - Uzbek order  "Karimov Firdavs Ismoil o'g'li" → "Karimov, F. I. o'g'li"
 *   - Western order "John Smith"                    → "Smith, J."
 */
function toScholarName(fullName: string): string {
  const raw = fullName.trim().split(/\s+/).filter(Boolean)
  if (raw.length < 2) return fullName.trim()

  // Peel off trailing patronymic tokens (o'g'li, qizi, ...) to keep them intact
  const patronymic: string[] = []
  const parts = [...raw]
  while (parts.length > 1 && UZ_PATRONYMIC.test(parts[parts.length - 1])) {
    patronymic.unshift(parts.pop() as string)
  }
  if (parts.length < 2) return fullName.trim()

  // If a patronymic was present, assume Uzbek order — surname is the first token.
  // Otherwise, Western order — surname is the last token.
  let last: string
  let givens: string[]
  if (patronymic.length > 0) {
    last = parts[0]
    givens = parts.slice(1)
  } else {
    last = parts[parts.length - 1]
    givens = parts.slice(0, -1)
  }

  const initials = givens.map(p => p.charAt(0).toUpperCase() + '.').join(' ')
  const tail = patronymic.length ? ` ${patronymic.join(' ')}` : ''
  return initials ? `${last}, ${initials}${tail}` : `${last}${tail}`
}

// Unified list of all authors — main (article.author) + co-authors, in one flat array.
// Each entry normalized to the same shape for rendering.
type FlatAuthor = {
  id: string
  fullName: string
  affiliation?: string
  country?: string
  orcidId?: string
  isCorresponding: boolean
  isPrimary: boolean
}

const authors = computed<FlatAuthor[]>(() => {
  const a = article.value
  if (!a) return []
  const out: FlatAuthor[] = []
  if (a.author && !isSystemAccount(a.author.role)) {
    out.push({
      id: `main-${a.author.id}`,
      fullName: a.author.full_name,
      affiliation: a.author.affiliation,
      country: a.author.country,
      orcidId: a.author.orcid_id,
      isCorresponding: true, // main author is corresponding by default
      isPrimary: true,
    })
  }
  ;(a.co_authors ?? []).forEach((co: ArticleAuthor) => {
    const name = co.user?.full_name || co.guest_name
    if (!name) return
    out.push({
      id: co.id,
      fullName: name,
      affiliation: co.user?.affiliation || co.guest_affiliation,
      country: co.user?.country,
      orcidId: co.user?.orcid_id || co.guest_orcid,
      isCorresponding: !!co.is_corresponding,
      isPrimary: false,
    })
  })
  // If no primary yet (main was filtered), promote first co-author as primary *visually*.
  if (out.length && !out.some(x => x.isPrimary)) {
    out[0].isPrimary = true
    out[0].isCorresponding = out[0].isCorresponding || true
  }
  return out
})

function applyAllMeta() {
  const a = article.value
  if (!a) return
  const titleEn = (a.title as any)?.en || (a.title as any)?.uz || ''
  const abstractEn = (a.abstract as any)?.en || (a.abstract as any)?.uz || ''
  const kwList = normalizeKeywords(a.keywords, localeStore.current)
  applySeo({
    title: titleEn,
    description: abstractEn.slice(0, 160),
    keywords: kwList.join(', '),
    ogImage: `/api/og-image/${a.id}`,
    ogUrl: `${window.location.origin}/articles/${a.id}`,
    canonical: `${window.location.origin}/articles/${a.id}`,
    type: 'article',
  })
  const brand = { siteName: siteInfo.siteName, issn: siteInfo.issn, logoUrl: siteInfo.logoUrl }
  injectLd([
    buildScholarlyArticle(a, brand),
    buildBreadcrumb([
      { name: 'Home', url: '/' },
      { name: 'Articles', url: '/articles' },
      { name: titleEn, url: `/articles/${a.id}` },
    ]),
  ])

  const journalTitle = siteInfo.siteName
  const issn = siteInfo.issn || undefined

  const authorNames = authors.value.map(au => toScholarName(au.fullName))

  const pdfUrl = a.pdf_file_path
    ? (a.pdf_file_path.startsWith('/') ? a.pdf_file_path : `/api/uploads/${a.pdf_file_path}`)
    : undefined

  let firstpage: string | undefined
  let lastpage: string | undefined
  if (a.pages) {
    const m = a.pages.match(/^\s*(\d+)\s*[-–—]\s*(\d+)\s*$/)
    if (m) { firstpage = m[1]; lastpage = m[2] }
    else firstpage = a.pages.trim()
  }

  applyCitationMeta({
    title: titleEn,
    authors: authorNames,
    publicationDate: a.published_date || a.created_at,
    journalTitle,
    issn,
    volume: a.volume?.number,
    issue: a.issue?.number,
    firstpage,
    lastpage,
    doi: a.doi || undefined,
    pdfUrl,
    abstractHtmlUrl: `/articles/${a.id}`,
    language: a.language,
    keywords: kwList,
    publisher: journalTitle,
  })
}

watch(article, applyAllMeta)
watch(homeSettings, applyAllMeta)

const articleId = computed(() => route.params.id as string)

const title = computed(() => article.value ? getLocalizedField(article.value.title, localeStore.current, '') : '')
const abstract = computed(() => article.value ? getLocalizedField(article.value.abstract, localeStore.current, '') : '')
const keywords = computed(() => normalizeKeywords(article.value?.keywords, localeStore.current))
const references = computed(() => normalizeKeywords(article.value?.references as any, localeStore.current))
const referencesExpanded = ref(false)
const REFERENCES_COLLAPSED_COUNT = 8
const visibleReferences = computed(() =>
  referencesExpanded.value ? references.value : references.value.slice(0, REFERENCES_COLLAPSED_COUNT)
)

const langMap: Record<string, string> = { uz: "O'zbek", ru: 'Русский', en: 'English' }
const langLabel = computed(() => article.value ? (langMap[article.value.language] ?? article.value.language.toUpperCase()) : '')

async function load() {
  loading.value = true
  error.value = false
  try {
    if (!homeSettings.value) {
      api.get<HomeSettingsData>('/api/home-settings').then(hs => { homeSettings.value = hs }).catch(() => {})
    }
    article.value = await api.get<Article>(`/api/articles/${articleId.value}`)
    api.post(`/api/articles/${articleId.value}/view`).catch(() => {})
    if (article.value.category_id) {
      const res = await api.get<PaginatedResponse<Article>>(
        `/api/articles?category_id=${article.value.category_id}&limit=3&status=published`
      )
      related.value = res.items.filter((a) => a.id !== articleId.value).slice(0, 3)
    }
  } catch (e: any) {
    if (e?.response?.status === 404) router.replace({ name: 'not-found' })
    else error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function copyLink() {
  await navigator.clipboard.writeText(window.location.href)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function shareTelegram() {
  const url = encodeURIComponent(window.location.href)
  const text = encodeURIComponent(title.value)
  window.open(`https://t.me/share/url?url=${url}&text=${text}`, '_blank')
}

async function downloadPdf() {
  if (!article.value) return
  try {
    const { download_url } = await api.get<{ download_url: string }>(`/api/articles/${article.value.id}/download`)
    const a = document.createElement('a')
    a.href = download_url
    a.target = '_blank'
    a.rel = 'noopener noreferrer'
    a.click()
  } catch {
    if (article.value.pdf_file_path) {
      const path = article.value.pdf_file_path.startsWith('/') ? article.value.pdf_file_path : `/api/uploads/${article.value.pdf_file_path}`
      window.open(path, '_blank')
    }
  }
}

const citationText = computed(() => {
  const a = article.value
  if (!a) return ''

  const authorStr = authors.value.map(au => toScholarName(au.fullName)).join(', ')

  const articleTitle = (a.title as any)?.en || (a.title as any)?.uz || 'Untitled'
  const year = a.published_date ? new Date(a.published_date).getFullYear() : ''
  const journalName = siteInfo.siteName
  const volIss = a.volume
    ? `${a.volume.number}${a.issue ? `(${a.issue.number})` : ''}`
    : ''
  const pages = a.pages || ''
  const doi = a.doi ? `https://doi.org/${a.doi}` : ''

  const articleUrl = typeof window !== 'undefined' ? window.location.href : `/articles/${a.id}`
  let citation = ''
  if (authorStr) citation += `${authorStr} `
  if (year) citation += `(${year}). `
  citation += `${articleTitle}. ${journalName}`
  if (volIss) citation += `, ${volIss}`
  if (pages) citation += `, ${pages}`
  citation += '.'
  if (doi) citation += ` ${doi}`
  citation += `\n${articleUrl}`
  return citation
})

async function copyCitation() {
  await navigator.clipboard.writeText(citationText.value)
  citationCopied.value = true
  setTimeout(() => { citationCopied.value = false }, 2000)
}

const pdfHref = computed(() => {
  const p = article.value?.pdf_file_path
  if (!p) return ''
  return p.startsWith('/') ? p : `/api/uploads/${p}`
})
</script>

<template>
  <div class="mx-auto max-w-5xl space-y-6">

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="skeleton h-4 w-48" />
      <div class="skeleton h-10 w-3/4 rounded-lg" />
      <div class="skeleton h-6 w-1/2 rounded-lg" />
      <div class="skeleton h-40 rounded-xl" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="flex flex-col items-center justify-center py-32">
      <AlertCircle :size="48" class="text-red-400" />
      <p class="mt-4 text-lg font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4" @click="load">
        <RefreshCw :size="15" />
        {{ t('common.retry') }}
      </button>
    </div>

    <template v-else-if="article">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
        <RouterLink to="/" class="hover:text-primary-700 dark:hover:text-primary-300">{{ t('nav.home') }}</RouterLink>
        <ChevronRight :size="14" />
        <RouterLink to="/archive" class="hover:text-primary-700 dark:hover:text-primary-300">{{ t('nav.archive') }}</RouterLink>
        <ChevronRight :size="14" />
        <span class="truncate text-journal-800 dark:text-primary-300 max-w-xs">{{ t('nav.articles') }}</span>
      </nav>

      <!-- ── Hero card: title + authors + meta + actions ── -->
      <section class="overflow-hidden rounded-2xl border border-primary-200 bg-white shadow-sm dark:border-primary-900/50 dark:bg-slate-800">
        <div class="h-1.5 bg-gradient-to-r from-primary-500 via-primary-600 to-primary-800" />

        <div class="p-6 sm:p-8">
          <!-- Title -->
          <h1 class="flex items-start gap-3 font-serif text-2xl font-bold leading-tight text-slate-900 dark:text-white sm:text-3xl">
            <BadgeCheck :size="28" class="mt-1 shrink-0 text-primary-500" />
            <span>{{ title }}</span>
          </h1>

          <!-- Unified authors list — row by row -->
          <ul v-if="authors.length" class="mt-5 space-y-2 border-l-2 border-primary-200 pl-4 dark:border-primary-900/50">
            <li v-for="au in authors" :key="au.id" class="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
              <span class="font-serif text-[15px] font-semibold text-slate-900 dark:text-white">
                {{ au.fullName }}
              </span>
              <span
                v-if="au.isCorresponding"
                class="rounded bg-primary-100 px-1.5 py-px text-[10px] font-bold uppercase tracking-wide text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                :title="t('author.submit.corresponding')"
              >
                *
              </span>
              <span v-if="au.affiliation" class="text-sm text-slate-500 dark:text-slate-400">
                — {{ au.affiliation }}<span v-if="au.country"> · {{ au.country }}</span>
              </span>
              <a
                v-if="au.orcidId"
                :href="`https://orcid.org/${au.orcidId}`"
                target="_blank"
                rel="noopener noreferrer"
                class="ml-auto inline-flex items-center gap-1 text-xs text-[#a6ce39] hover:underline"
              >
                <svg viewBox="0 0 100 100" class="h-4 w-4"><circle cx="50" cy="50" r="48" fill="#a6ce39"/><path d="M 22 50 L 45 50 L 45 22" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M 78 50 L 55 50 L 55 78" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/></svg>
                {{ au.orcidId }}
              </a>
            </li>
          </ul>

          <!-- Meta badges row -->
          <div class="mt-6 flex flex-wrap items-center gap-2">
            <span
              v-if="article.published_date"
              class="inline-flex items-center gap-1.5 rounded-md bg-slate-800 px-3 py-1 text-xs font-medium text-white dark:bg-slate-900"
            >
              <Calendar :size="12" />{{ formatDate(article.published_date) }}
            </span>
            <span
              v-if="article.volume"
              class="inline-flex items-center gap-1.5 rounded-md bg-slate-800 px-3 py-1 text-xs font-medium text-white dark:bg-slate-900"
            >
              <BookOpen :size="12" />Volume {{ article.volume.number }}<span v-if="article.issue"> Issue {{ article.issue.number }}</span>
            </span>
            <span
              v-if="article.pages"
              class="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200"
            >
              <Hash :size="12" />{{ article.pages }}
            </span>
            <span
              class="inline-flex items-center gap-1.5 rounded-md bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700 dark:bg-slate-700 dark:text-slate-200"
            >
              <Globe :size="12" />{{ langLabel }}
            </span>
            <span
              v-if="article.article_type"
              class="inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 dark:bg-amber-950/30 dark:text-amber-300"
            >
              {{ t(`admin.articles.type_${article.article_type}`) }}
            </span>

            <!-- Stats on the right -->
            <span class="ml-auto flex items-center gap-3 text-xs text-slate-400">
              <span class="inline-flex items-center gap-1"><Eye :size="13" />{{ article.view_count.toLocaleString() }}</span>
              <span class="inline-flex items-center gap-1"><Download :size="13" />{{ article.download_count.toLocaleString() }}</span>
            </span>
          </div>

          <!-- DOI -->
          <div v-if="article.doi" class="mt-5">
            <a
              :href="`https://doi.org/${article.doi}`"
              target="_blank"
              rel="noopener noreferrer"
              class="inline-flex items-center gap-2 rounded-md bg-[#fcb425]/10 px-3 py-1.5 text-sm font-medium text-[#b37400] hover:bg-[#fcb425]/20 dark:bg-[#fcb425]/10 dark:text-amber-300"
            >
              <span class="flex h-5 items-center justify-center rounded bg-[#fcb425] px-1.5 text-[10px] font-black text-white">DOI</span>
              <span class="font-mono">https://doi.org/{{ article.doi }}</span>
            </a>
          </div>

          <!-- PDF actions -->
          <div v-if="article.pdf_file_path" class="mt-6 flex flex-wrap items-center gap-2">
            <button
              class="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700"
              @click="showPdfPreview = true"
            >
              <FileText :size="16" />
              Full text (PDF)
            </button>
            <button
              class="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700"
              @click="downloadPdf"
            >
              <Download :size="16" />
              {{ t('article.download_pdf') }}
            </button>
          </div>
        </div>
      </section>

      <!-- ── Abstract ── -->
      <section class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/40">
        <header class="flex items-center gap-2 border-b border-slate-200 bg-white px-6 py-3 dark:border-slate-700 dark:bg-slate-800/60">
          <FileText :size="18" class="text-primary-600 dark:text-primary-400" />
          <h2 class="font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
            {{ t('article.abstract') }}
          </h2>
        </header>
        <div class="px-6 py-5">
          <ArticleAbstract :text="abstract" />
        </div>
      </section>

      <!-- ── Keywords ── -->
      <section v-if="keywords.length" class="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-3 flex items-center gap-2">
          <Tag :size="16" class="text-primary-600 dark:text-primary-400" />
          <h2 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">
            {{ t('article.keywords') }}
          </h2>
        </div>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="kw in keywords"
            :key="kw"
            class="inline-flex items-center gap-1 rounded-full bg-primary-50 px-3 py-1 text-sm text-primary-700 transition hover:bg-primary-100 dark:bg-primary-950/40 dark:text-primary-300"
          >
            {{ kw }}
          </span>
        </div>
      </section>

      <!-- ── References ── -->
      <section v-if="references.length" class="overflow-hidden rounded-2xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-800">
        <header class="flex items-center gap-2 border-b border-slate-200 bg-slate-50 px-6 py-3 dark:border-slate-700 dark:bg-slate-800/60">
          <Users :size="18" class="text-primary-600 dark:text-primary-400" />
          <h2 class="font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
            {{ t('article.references') }}
          </h2>
          <span class="ml-auto text-xs text-slate-400">{{ references.length }}</span>
        </header>
        <div class="px-6 py-5">
          <ul class="space-y-3 text-[15px] leading-7 text-slate-700 dark:text-slate-200">
            <li
              v-for="(ref, i) in visibleReferences"
              :key="i"
              class="whitespace-pre-wrap border-l-2 border-transparent pl-3 hover:border-primary-400"
            >{{ ref }}</li>
          </ul>
          <button
            v-if="references.length > REFERENCES_COLLAPSED_COUNT"
            class="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-primary-700 transition hover:bg-primary-50 dark:border-slate-600 dark:bg-slate-800 dark:text-primary-300 dark:hover:bg-slate-700"
            @click="referencesExpanded = !referencesExpanded"
          >
            {{ referencesExpanded ? t('article.show_less') : t('article.show_more') }}
          </button>
        </div>
      </section>

      <!-- ── How to cite ── -->
      <section class="overflow-hidden rounded-2xl border border-primary-200 bg-gradient-to-br from-primary-50 to-white dark:border-primary-900/50 dark:from-primary-950/30 dark:to-slate-800">
        <header class="flex items-center gap-2 border-b border-primary-200 px-6 py-3 dark:border-primary-900/50">
          <BookOpen :size="18" class="text-primary-600 dark:text-primary-400" />
          <h2 class="font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
            {{ t('article.cite') }}
          </h2>
          <button
            class="ml-auto inline-flex items-center gap-1.5 rounded-lg border border-primary-200 bg-white px-3 py-1.5 text-xs font-medium text-primary-700 transition hover:bg-primary-50 dark:border-primary-800 dark:bg-slate-800 dark:text-primary-300"
            @click="copyCitation"
          >
            <Check v-if="citationCopied" :size="13" class="text-green-500" />
            <Copy v-else :size="13" />
            {{ citationCopied ? t('article.copied') : 'Copy' }}
          </button>
        </header>
        <div class="px-6 py-4">
          <p class="whitespace-pre-line text-sm leading-relaxed text-slate-700 dark:text-slate-300">{{ citationText }}</p>
        </div>
      </section>

      <!-- ── Share ── -->
      <section class="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
        <div class="flex flex-wrap items-center gap-3">
          <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">
            {{ t('article.share') }}:
          </span>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-slate-600 transition hover:bg-slate-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
            @click="copyLink"
          >
            <Check v-if="copied" :size="13" class="text-green-500" />
            <Copy v-else :size="13" />
            {{ copied ? t('article.copied') : t('article.copy_link') }}
          </button>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border border-sky-200 bg-sky-50 px-3 py-1.5 text-sm text-sky-700 transition hover:bg-sky-100 dark:border-sky-900 dark:bg-sky-950/30 dark:text-sky-300"
            @click="shareTelegram"
          >
            <Send :size="13" />
            Telegram
          </button>
        </div>
      </section>

      <!-- ── Related articles ── -->
      <section v-if="related.length">
        <div class="mb-4 flex items-center gap-2">
          <h2 class="font-serif text-xl font-bold text-journal-800 dark:text-primary-300">{{ t('article.related') }}</h2>
        </div>
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <ArticleCard v-for="rel in related" :key="rel.id" :article="rel" />
        </div>
      </section>
    </template>

    <!-- PDF Preview Modal -->
    <PdfPreview
      v-if="showPdfPreview && pdfHref"
      :url="pdfHref"
      :title="title"
      @close="showPdfPreview = false"
    />
  </div>
</template>
