<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Download, Share2, Copy, Check, Eye, ChevronRight,
  BookOpen, Tag, Calendar, Globe, Hash, AlertCircle, RefreshCw, ChevronDown
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDate } from '@/utils/formatDate'
import type { Article, PaginatedResponse } from '@/types/article'
import AuthorsList from '@/components/article/AuthorsList.vue'
import ArticleAbstract from '@/components/article/ArticleAbstract.vue'
import CitationBox from '@/components/article/CitationBox.vue'
import ArticleCard from '@/components/article/ArticleCard.vue'
import CoverImage from '@/components/ui/CoverImage.vue'
import PdfPreview from '@/components/ui/PdfPreview.vue'
import { useSeoMeta, applyCitationMeta } from '@/composables/useSeoMeta'
import { useJsonLd } from '@/composables/useJsonLd'
import { buildScholarlyArticle, buildBreadcrumb } from '@/utils/jsonld'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()

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
const showCitation = ref(false)
const showPdfPreview = ref(false)
const homeSettings = ref<HomeSettingsData | null>(null)

const { apply: applySeo } = useSeoMeta()
const { inject: injectLd } = useJsonLd()

function applyAllMeta() {
  const a = article.value
  if (!a) return
  const titleEn = (a.title as any)?.en || (a.title as any)?.uz || ''
  const abstractEn = (a.abstract as any)?.en || (a.abstract as any)?.uz || ''
  applySeo({
    title: titleEn,
    description: abstractEn.slice(0, 160),
    keywords: Array.isArray(a.keywords) ? a.keywords.join(', ') : '',
    ogImage: `/api/og-image/${a.id}`,
    ogUrl: `https://scientists.uz/articles/${a.id}`,
    canonical: `https://scientists.uz/articles/${a.id}`,
    type: 'article',
  })
  injectLd([
    buildScholarlyArticle(a),
    buildBreadcrumb([
      { name: 'Home', url: '/' },
      { name: 'Articles', url: '/articles' },
      { name: titleEn, url: `/articles/${a.id}` },
    ]),
  ])

  // Google Scholar citation_* meta tags
  const hs = homeSettings.value
  const journalTitle = hs?.hero_title?.en || hs?.hero_title?.uz || hs?.hero_title?.ru || 'Science and Innovation'
  const issn = hs?.issn_online || hs?.issn_print || undefined

  const authors: string[] = []
  if (a.author?.full_name) authors.push(a.author.full_name)
  ;(a.co_authors || []).forEach((co: any) => {
    const name = co.user?.full_name || co.guest_name
    if (name) authors.push(name)
  })

  const pdfUrl = a.pdf_file_path
    ? (a.pdf_file_path.startsWith('/') ? a.pdf_file_path : `/api/uploads/${a.pdf_file_path}`)
    : undefined

  applyCitationMeta({
    title: titleEn,
    authors,
    publicationDate: a.published_date || a.created_at,
    journalTitle,
    issn,
    doi: a.doi || undefined,
    pdfUrl,
    abstractHtmlUrl: `/articles/${a.id}`,
    language: a.language,
    keywords: Array.isArray(a.keywords) ? a.keywords : [],
    publisher: journalTitle,
  })
}

watch(article, applyAllMeta)
watch(homeSettings, applyAllMeta)

const articleId = computed(() => route.params.id as string)

const title = computed(() => article.value ? getLocalizedField(article.value.title, localeStore.current, '') : '')
const abstract = computed(() => article.value ? getLocalizedField(article.value.abstract, localeStore.current, '') : '')
const keywords = computed(() => article.value?.keywords ?? [])

const langMap: Record<string, string> = { uz: "O'zbek", ru: 'Русский', en: 'English' }
const langLabel = computed(() => article.value ? (langMap[article.value.language] ?? article.value.language.toUpperCase()) : '')

async function load() {
  loading.value = true
  error.value = false
  try {
    // Load home settings in parallel (for journal name + ISSN)
    if (!homeSettings.value) {
      api.get<HomeSettingsData>('/api/home-settings').then(hs => { homeSettings.value = hs }).catch(() => {})
    }
    article.value = await api.get<Article>(`/api/articles/${articleId.value}`)
    // increment view (fire and forget)
    api.post(`/api/articles/${articleId.value}/view`).catch(() => {})
    // fetch related by category
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
    // fallback: direct path
    if (article.value.pdf_file_path) {
      const path = article.value.pdf_file_path.startsWith('/') ? article.value.pdf_file_path : `/api/uploads/${article.value.pdf_file_path}`
      window.open(path, '_blank')
    }
  }
}
</script>

<template>
  <div class="space-y-6">

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="animate-pulse space-y-4">
        <div class="h-4 w-48 rounded bg-stone-200 dark:bg-slate-700" />
        <div class="h-8 w-3/4 rounded-lg bg-stone-200 dark:bg-slate-700" />
        <div class="h-6 w-1/2 rounded-lg bg-stone-200 dark:bg-slate-700" />
      </div>
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

    <!-- Article content -->
    <template v-else-if="article">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
        <RouterLink to="/" class="hover:text-primary-700 dark:hover:text-primary-300">{{ t('nav.home') }}</RouterLink>
        <ChevronRight :size="14" />
        <RouterLink to="/archive" class="hover:text-primary-700 dark:hover:text-primary-300">{{ t('nav.archive') }}</RouterLink>
        <ChevronRight :size="14" />
        <span class="truncate text-journal-800 dark:text-primary-300 max-w-xs">{{ t('nav.articles') }}</span>
      </nav>

      <!-- Title & Authors -->
      <div>
        <h1 class="font-serif text-2xl font-bold leading-tight text-journal-900 dark:text-white sm:text-3xl">
          {{ title }}
        </h1>

        <!-- Main author + co-authors with ORCID -->
        <div class="mt-5 space-y-3">
          <div v-if="article.author" class="flex flex-col gap-0.5">
            <span class="text-sm font-semibold text-journal-800 dark:text-slate-200">
              {{ article.author.full_name }}
              <span class="text-primary-600 dark:text-primary-400">*</span>
            </span>
            <span v-if="article.author.affiliation" class="text-xs text-slate-500 dark:text-slate-400">{{ article.author.affiliation }}</span>
            <a
              v-if="article.author.orcid_id"
              :href="`https://orcid.org/${article.author.orcid_id}`"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-0.5 inline-flex items-center gap-1.5 text-xs text-[#a6ce39] hover:underline w-fit"
            >
              <svg viewBox="0 0 100 100" class="h-4 w-4"><circle cx="50" cy="50" r="48" fill="#a6ce39"/><path d="M 22 50 L 45 50 L 45 22" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M 78 50 L 55 50 L 55 78" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/></svg>
              https://orcid.org/{{ article.author.orcid_id }}
            </a>
          </div>
          <div v-for="co in article.co_authors ?? []" :key="co.id" class="flex flex-col gap-0.5">
            <span class="text-sm font-semibold text-journal-800 dark:text-slate-200">{{ co.user?.full_name || co.guest_name }}</span>
            <span v-if="co.user?.affiliation || co.guest_affiliation" class="text-xs text-slate-500 dark:text-slate-400">{{ co.user?.affiliation || co.guest_affiliation }}</span>
            <a
              v-if="co.user?.orcid_id || co.guest_orcid"
              :href="`https://orcid.org/${co.user?.orcid_id || co.guest_orcid}`"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-0.5 inline-flex items-center gap-1.5 text-xs text-[#a6ce39] hover:underline w-fit"
            >
              <svg viewBox="0 0 100 100" class="h-4 w-4"><circle cx="50" cy="50" r="48" fill="#a6ce39"/><path d="M 22 50 L 45 50 L 45 22" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/><path d="M 78 50 L 55 50 L 55 78" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/></svg>
              https://orcid.org/{{ co.user?.orcid_id || co.guest_orcid }}
            </a>
          </div>
        </div>

        <!-- DOI -->
        <div v-if="article.doi" class="mt-5">
          <a
            :href="`https://doi.org/${article.doi}`"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 text-sm text-primary-700 hover:underline dark:text-primary-400"
          >
            <span class="flex h-5 w-5 items-center justify-center rounded-full bg-primary-500 text-[10px] font-bold text-white">D</span>
            https://doi.org/{{ article.doi }}
          </a>
        </div>

        <!-- PDF / XML action buttons -->
        <div v-if="article.pdf_file_path" class="mt-6 flex flex-wrap items-center gap-2">
          <button
            class="inline-flex items-center gap-2 rounded-lg bg-primary-400 px-5 py-2.5 text-sm font-semibold text-journal-900 shadow-sm transition hover:bg-primary-500"
            @click="showPdfPreview = true"
          >
            <FileText :size="16" />
            Full text (PDF)
          </button>
          <button
            class="inline-flex items-center gap-2 rounded-lg bg-journal-800 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-journal-700"
            @click="downloadPdf"
          >
            <Download :size="16" />
            {{ t('article.download_pdf') }}
          </button>
        </div>
      </div>

      <!-- 2-col content -->
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_260px]">
        <div class="min-w-0 space-y-8">
            <!-- Abstract -->
            <section>
              <h2 class="mb-3 font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
                {{ t('article.abstract') }}
              </h2>
              <ArticleAbstract :text="abstract" />
            </section>

            <!-- Keywords -->
            <section v-if="keywords.length">
              <h2 class="mb-3 font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
                {{ t('article.keywords') }}
              </h2>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="kw in keywords"
                  :key="kw"
                  class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-sm text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
                >
                  <Tag :size="11" />
                  {{ kw }}
                </span>
              </div>
            </section>

            <!-- Authors full -->
            <section>
              <h2 class="mb-4 font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
                {{ t('article.authors') }}
              </h2>
              <AuthorsList :authors="article.co_authors ?? []" :main-author="article.author" />
            </section>

            <!-- References -->
            <section v-if="article.references && article.references.length">
              <h2 class="mb-4 font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
                {{ t('article.references') }}
              </h2>
              <ol class="space-y-2 text-sm text-slate-600 dark:text-slate-300">
                <li
                  v-for="(ref, i) in article.references"
                  :key="i"
                  class="flex gap-2 leading-relaxed"
                >
                  <span class="shrink-0 font-mono text-xs text-slate-400">[{{ i + 1 }}]</span>
                  <span>{{ ref }}</span>
                </li>
              </ol>
            </section>

            <!-- Citation -->
            <section>
              <button
                class="flex w-full items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-5 py-4 text-left dark:border-slate-700 dark:bg-slate-900"
                @click="showCitation = !showCitation"
              >
                <div class="flex items-center gap-2 font-serif font-semibold text-slate-900 dark:text-white">
                  <BookOpen :size="18" />
                  {{ t('article.cite') }}
                </div>
                <ChevronDown
                  :size="18"
                  class="text-slate-400 transition-transform"
                  :class="{ 'rotate-180': showCitation }"
                />
              </button>
              <Transition
                enter-active-class="transition-all duration-200 ease-out"
                enter-from-class="opacity-0 -translate-y-2"
                leave-active-class="transition-all duration-150 ease-in"
                leave-to-class="opacity-0 -translate-y-2"
              >
                <div v-if="showCitation" class="mt-2">
                  <CitationBox :article="article" />
                </div>
              </Transition>
            </section>
          </div>

          <!-- ─── Right: sticky sidebar ─── -->
          <aside class="lg:sticky lg:top-24 lg:self-start space-y-4">

            <!-- Cover card -->
            <div class="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
              <div class="aspect-[3/4] bg-gradient-to-br from-primary-600 to-primary-800">
                <img
                  v-if="article.cover_image_url"
                  :src="article.cover_image_url.startsWith('/') ? article.cover_image_url : `/api/uploads/${article.cover_image_url}`"
                  :alt="title"
                  class="h-full w-full object-cover"
                />
                <div v-else class="flex h-full w-full flex-col items-center justify-center p-5 text-center">
                  <BookOpen :size="40" class="mb-3 text-white/30" />
                  <span class="font-serif text-sm font-bold text-white/90 line-clamp-3">{{ title }}</span>
                </div>
              </div>
              <div class="p-4 text-xs">
                <div v-if="article.published_date" class="mb-2">
                  <p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{{ t('articles.published') }}</p>
                  <p class="mt-0.5 font-semibold text-journal-800 dark:text-slate-200">{{ formatDate(article.published_date) }}</p>
                </div>
                <div class="mb-2">
                  <p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{{ t('articles.filter_language') }}</p>
                  <p class="mt-0.5 font-semibold text-journal-800 dark:text-slate-200">{{ langLabel }}</p>
                </div>
                <div v-if="article.article_type" class="mb-2">
                  <p class="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{{ t('article.type') }}</p>
                  <p class="mt-0.5 font-semibold text-journal-800 dark:text-slate-200">{{ t(`admin.articles.type_${article.article_type}`) }}</p>
                </div>
                <div class="mt-3 grid grid-cols-2 gap-2 border-t border-stone-100 pt-3 dark:border-slate-700">
                  <div class="flex flex-col items-center">
                    <Eye :size="14" class="text-primary-600 dark:text-primary-400" />
                    <span class="mt-0.5 text-sm font-bold text-journal-800 dark:text-slate-200">{{ article.view_count.toLocaleString() }}</span>
                    <span class="text-[10px] text-slate-400">{{ t('articles.views') }}</span>
                  </div>
                  <div class="flex flex-col items-center">
                    <Download :size="14" class="text-primary-600 dark:text-primary-400" />
                    <span class="mt-0.5 text-sm font-bold text-journal-800 dark:text-slate-200">{{ article.download_count.toLocaleString() }}</span>
                    <span class="text-[10px] text-slate-400">{{ t('articles.downloads') }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Share -->
            <div class="rounded-xl border border-stone-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800">
              <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                {{ t('article.share') }}
              </p>
              <div class="flex gap-2">
                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-stone-200 py-2 text-xs text-slate-600 transition hover:bg-stone-50 dark:border-slate-600 dark:text-slate-400 dark:hover:bg-slate-700"
                  @click="copyLink"
                >
                  <Check v-if="copied" :size="13" class="text-green-500" />
                  <Copy v-else :size="13" />
                  {{ copied ? t('article.copied') : t('article.copy_link') }}
                </button>
                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-blue-200 py-2 text-xs text-blue-600 transition hover:bg-blue-50 dark:border-blue-900 dark:text-blue-400 dark:hover:bg-blue-950/30"
                  @click="shareTelegram"
                >
                  <Share2 :size="14" />
                  Telegram
                </button>
              </div>
            </div>
          </aside>
        </div>

      <!-- Related articles -->
      <section v-if="related.length" class="mt-8 border-t border-stone-200 pt-8 dark:border-slate-700">
        <h2 class="mb-4 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">{{ t('article.related') }}</h2>
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <ArticleCard v-for="rel in related" :key="rel.id" :article="rel" />
        </div>
      </section>
    </template>

    <!-- PDF Preview Modal -->
    <PdfPreview
      v-if="showPdfPreview && article?.pdf_file_path"
      :url="article.pdf_file_path.startsWith('/') ? article.pdf_file_path : `/api/uploads/${article.pdf_file_path}`"
      :title="title"
      @close="showPdfPreview = false"
    />
  </div>
</template>
