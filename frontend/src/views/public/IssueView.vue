<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  BookOpen, Calendar, FileText, ChevronRight,
  AlertCircle, RefreshCw, Download, Tag,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import type { Article, PaginatedResponse } from '@/types/article'
import type { Issue, Volume } from '@/types/volume'
import { formatDate } from '@/utils/formatDate'
import ArticleCard from '@/components/article/ArticleCard.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

interface Category { id: string; slug: string; name_uz: string; name_ru: string; name_en: string }

const { t } = useI18n()
const route = useRoute()
const localeStore = useLocaleStore()

const { apply: applySeo } = useSeoMeta()

const volumeId = computed(() => route.params.volumeId as string)
const issueId = computed(() => route.params.issueId as string)

const volume = ref<Volume | null>(null)
const issue = ref<Issue | null>(null)
const articles = ref<Article[]>([])
const categories = ref<Category[]>([])
const total = ref(0)
const loading = ref(true)
const error = ref(false)

function categoryName(c: Category | { name_uz: string; name_ru: string; name_en: string }) {
  return (c as any)[`name_${localeStore.current}`] || c.name_uz || c.name_en
}

const fullPdfHref = computed(() => {
  const u = (issue.value as any)?.full_pdf_url as string | undefined
  if (!u) return ''
  return u.startsWith('http') || u.startsWith('/') ? u : `/api/uploads/${u}`
})

// Group all issue articles by category (ordered by page number within each group).
const groupedSections = computed(() => {
  const map = new Map<string, { category: Category | null; items: Article[] }>()
  for (const c of categories.value) {
    map.set(c.id, { category: c, items: [] })
  }
  const uncategorized: Article[] = []
  for (const a of articles.value) {
    if (a.category && map.has(a.category.id)) {
      map.get(a.category.id)!.items.push(a)
    } else {
      uncategorized.push(a)
    }
  }
  const sections: { category: Category | null; items: Article[] }[] = []
  for (const v of map.values()) {
    if (v.items.length) sections.push(v)
  }
  if (uncategorized.length) sections.push({ category: null, items: uncategorized })
  return sections
})

async function load() {
  loading.value = true
  error.value = false
  try {
    // Fetch all articles in the issue (sorted by pages), volume, and categories.
    const [volumeData, articlesData, categoriesData] = await Promise.all([
      api.get<Volume>(`/api/volumes/${volumeId.value}`),
      api.get<PaginatedResponse<Article>>(
        `/api/articles?issue_id=${issueId.value}&page=1&limit=200&status=published&sort=pages`
      ),
      api.get<Category[]>('/api/categories').catch(() => []),
    ])
    volume.value = volumeData
    issue.value = volumeData.issues.find((i) => i.id === issueId.value) ?? null
    articles.value = articlesData.items
    total.value = articlesData.total
    categories.value = categoriesData ?? []
    if (volumeData && issue.value) {
      applySeo({
        title: `Vol. ${volumeData.number}, Issue ${issue.value.number} (${volumeData.year})`,
        ogUrl: `${window.location.origin}/archive/${volumeData.id}/issues/${issue.value.id}`,
        canonical: `${window.location.origin}/archive/${volumeData.id}/issues/${issue.value.id}`,
      })
    }
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">

    <!-- Error -->
    <div v-if="error" class="flex flex-col items-center justify-center py-32">
      <AlertCircle :size="40" class="text-red-400" />
      <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
    </div>

    <template v-else>
      <!-- Header -->
      <div class="relative overflow-hidden border-b border-slate-200 bg-gradient-to-br from-slate-900 via-primary-950 to-slate-900 py-10">
        <div class="absolute inset-0">
          <img src="https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=1920&q=80&auto=format" alt="" class="h-full w-full object-cover opacity-10" />
          <div class="absolute inset-0 bg-gradient-to-b from-slate-900/60 via-primary-950/80 to-slate-900" />
        </div>
        <div class="relative mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <!-- Breadcrumb -->
          <nav v-if="!loading" class="mb-4 flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
            <RouterLink to="/" class="text-slate-400 hover:text-white">{{ t('nav.home') }}</RouterLink>
            <ChevronRight :size="14" class="text-slate-500" />
            <RouterLink to="/archive" class="text-slate-400 hover:text-white">{{ t('archive.title') }}</RouterLink>
            <ChevronRight :size="14" class="text-slate-500" />
            <span class="text-slate-200" v-if="volume && issue">
              Vol. {{ volume.number }}, Issue {{ issue.number }}
            </span>
          </nav>

          <!-- Skeleton header -->
          <div v-if="loading" class="space-y-3">
            <div class="skeleton h-4 w-64 rounded" />
            <div class="skeleton h-8 w-80 rounded-lg" />
            <div class="skeleton h-4 w-48 rounded" />
          </div>

          <!-- Issue info -->
          <div v-else-if="volume && issue" class="flex items-start gap-5">
            <div class="hidden h-20 w-20 items-center justify-center rounded-xl bg-white/10 backdrop-blur sm:flex">
              <BookOpen :size="32" class="text-primary-300" />
            </div>
            <div class="min-w-0 flex-1">
              <h1 class="font-serif text-3xl font-bold text-white sm:text-4xl">
                Vol. {{ volume.number }}, {{ t('archive.issue_label', { number: issue.number }) }}
              </h1>
              <div class="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-300">
                <span v-if="issue.published_date" class="inline-flex items-center gap-1.5">
                  <Calendar :size="14" />{{ formatDate(issue.published_date) }}
                </span>
                <span class="inline-flex items-center gap-1.5">
                  <FileText :size="14" />{{ total }} {{ t('archive.articles') }}
                </span>
              </div>
              <p v-if="issue.description" class="mt-3 text-sm text-slate-300">
                {{ issue.description }}
              </p>

              <!-- Full issue PDF -->
              <a
                v-if="fullPdfHref"
                :href="fullPdfHref"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-5 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg transition hover:bg-emerald-700"
              >
                <Download :size="16" />
                Sonni to'liq PDF yuklab olish
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Articles, grouped by category -->
      <div class="mx-auto max-w-5xl space-y-10 px-4 py-8 sm:px-6 lg:px-8">

        <!-- Skeleton -->
        <div v-if="loading" class="flex flex-col gap-4">
          <div v-for="i in 5" :key="i" class="skeleton h-40 rounded-xl" />
        </div>

        <!-- Empty -->
        <div v-else-if="articles.length === 0" class="flex flex-col items-center py-20">
          <FileText :size="48" class="text-slate-200 dark:text-slate-700" />
          <p class="mt-4 text-slate-400">{{ t('archive.no_articles_in_issue') }}</p>
        </div>

        <!-- Categorized sections -->
        <section v-for="section in groupedSections" v-else :key="section.category?.id || 'uncat'">
          <div class="mb-4 flex items-baseline gap-3 border-b-2 border-primary-400 pb-2">
            <Tag :size="16" class="text-primary-600 dark:text-primary-400" />
            <h2 class="font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
              {{ section.category ? categoryName(section.category) : 'Boshqalar' }}
            </h2>
            <span class="text-xs font-medium text-slate-400">{{ section.items.length }} ta maqola</span>
          </div>
          <div class="flex flex-col gap-4">
            <ArticleCard
              v-for="article in section.items"
              :key="article.id"
              :article="article"
            />
          </div>
        </section>
      </div>
    </template>
  </div>
</template>
