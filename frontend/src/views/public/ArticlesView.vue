<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Search as SearchIcon, AlertCircle, RefreshCw, Globe,
  BookOpen as BookOpenIcon, ArrowUpDown, Tag as TagIcon, X,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import type { Article, PaginatedResponse } from '@/types/article'
import type { Volume } from '@/types/volume'
import ArticleCard from '@/components/article/ArticleCard.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

interface Category { id: string; slug: string; name_uz: string; name_ru: string; name_en: string }

const { t } = useI18n()
useSeoMeta({
  title: t('nav.articles'),
  canonical: `${window.location.origin}/articles`,
  ogUrl: `${window.location.origin}/articles`,
})

const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()

const articles = ref<Article[]>([])
const volumes = ref<Volume[]>([])
const categories = ref<Category[]>([])
const total = ref(0)
const pages = ref(1)
const loading = ref(false)
const error = ref(false)

const filters = reactive({
  search: (route.query.q as string) ?? '',
  language: (route.query.language as string) ?? '',
  volume_id: (route.query.volume as string) ?? '',
  category: (route.query.category as string) ?? '',
  sort: (route.query.sort as string) ?? 'newest',
  page: Number(route.query.page) || 1,
})

const PAGE_SIZE = 24

const sortOptions = computed(() => [
  { value: 'newest', label: t('articles.sort_newest') },
  { value: 'oldest', label: t('articles.sort_oldest') },
  { value: 'pages', label: "Sahifa raqami bo'yicha" },
  { value: 'downloads', label: t('articles.sort_downloads') },
])

const hasActiveFilters = computed(() =>
  !!(filters.search || filters.language || filters.volume_id || filters.category || filters.sort !== 'newest')
)

function categoryName(c: Category | { name_uz: string; name_ru: string; name_en: string }) {
  return (c as any)[`name_${localeStore.current}`] || c.name_uz || c.name_en
}

// Group articles by category for display.
const grouped = computed(() => {
  const map = new Map<string, { category: Category | null; items: Article[] }>()
  // ensure ordering follows categories.value (catalog order) for filter clarity
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

const showGrouped = computed(() => !filters.category && grouped.value.length > 1)

async function fetchArticles() {
  loading.value = true
  error.value = false
  try {
    const params = new URLSearchParams()
    params.set('page', String(filters.page))
    params.set('limit', String(PAGE_SIZE))
    params.set('status', 'published')
    if (filters.search) params.set('search', filters.search)
    if (filters.language) params.set('lang', filters.language)
    if (filters.volume_id) params.set('volume_id', filters.volume_id)
    if (filters.category) params.set('category', filters.category)
    if (filters.sort === 'oldest') params.set('sort', 'oldest')
    else if (filters.sort === 'downloads') params.set('sort', 'downloads')
    else if (filters.sort === 'pages') params.set('sort', 'pages')

    const data = await api.get<PaginatedResponse<Article>>(`/api/articles?${params}`)
    articles.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function fetchVolumes() {
  try { volumes.value = await api.get<Volume[]>('/api/volumes') } catch {}
}

async function fetchCategories() {
  try { categories.value = await api.get<Category[]>('/api/categories') } catch {}
}

onMounted(() => { fetchVolumes(); fetchCategories(); fetchArticles() })

watch(
  () => ({ ...filters }),
  () => {
    router.replace({
      query: {
        ...(filters.search && { q: filters.search }),
        ...(filters.language && { language: filters.language }),
        ...(filters.volume_id && { volume: filters.volume_id }),
        ...(filters.category && { category: filters.category }),
        ...(filters.sort !== 'newest' && { sort: filters.sort }),
        ...(filters.page > 1 && { page: String(filters.page) }),
      },
    })
    fetchArticles()
  },
  { deep: true }
)

watch(() => route.query.category, (newCat) => {
  if (typeof newCat === 'string' && newCat !== filters.category) {
    filters.category = newCat
    filters.page = 1
  } else if (!newCat && filters.category) {
    filters.category = ''
    filters.page = 1
  }
})

function clearFilters() {
  filters.search = ''
  filters.language = ''
  filters.volume_id = ''
  filters.category = ''
  filters.sort = 'newest'
  filters.page = 1
}

let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput(e: Event) {
  const v = (e.target as HTMLInputElement).value
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { filters.search = v; filters.page = 1 }, 300)
}

function onPageChange(p: number) {
  filters.page = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const langOptions = [
  { value: '', label: () => t('common.all') },
  { value: 'uz', label: () => "O'zbek" },
  { value: 'ru', label: () => 'Русский' },
  { value: 'en', label: () => 'English' },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('articles.title') }}</h1>
      <p v-if="!loading" class="mt-1 text-sm text-slate-300">
        {{ t('articles.total_count', { count: total }) }}
      </p>
    </section>

    <!-- Category chips row -->
    <section v-if="categories.length" class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div class="flex flex-wrap items-center gap-2">
        <button
          class="rounded-full px-3 py-1.5 text-xs font-semibold transition"
          :class="!filters.category
            ? 'bg-primary-600 text-white shadow-sm'
            : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'"
          @click="() => { filters.category = ''; filters.page = 1 }"
        >
          {{ t('common.all') }}
        </button>
        <button
          v-for="c in categories"
          :key="c.id"
          class="inline-flex items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-semibold transition"
          :class="filters.category === c.slug
            ? 'bg-primary-600 text-white shadow-sm'
            : 'bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600'"
          @click="() => { filters.category = c.slug; filters.page = 1 }"
        >
          <TagIcon :size="11" />{{ categoryName(c) }}
        </button>
      </div>
    </section>

    <!-- Top filter bar: search + language + volume + sort -->
    <section class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
      <div class="flex flex-wrap items-center gap-3">
        <!-- Search -->
        <div class="relative min-w-[200px] flex-1">
          <SearchIcon :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            :value="filters.search"
            :placeholder="t('articles.search_placeholder')"
            class="input-base pl-9"
            @input="onSearchInput"
          />
        </div>

        <!-- Language -->
        <div class="flex items-center gap-1 rounded-lg border border-slate-200 bg-white p-1 dark:border-slate-700 dark:bg-slate-800">
          <Globe :size="13" class="ml-1 text-slate-400" />
          <button
            v-for="lang in langOptions"
            :key="lang.value"
            class="rounded-md px-2.5 py-1 text-xs font-medium transition"
            :class="filters.language === lang.value
              ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
              : 'text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:bg-slate-700'"
            @click="() => { filters.language = lang.value; filters.page = 1 }"
          >{{ lang.label() }}</button>
        </div>

        <!-- Volume -->
        <div class="flex items-center gap-1.5">
          <BookOpenIcon :size="13" class="text-slate-400" />
          <select v-model="filters.volume_id" class="input-base h-9 w-auto py-1 text-xs" @change="filters.page = 1">
            <option value="">Barcha jildlar</option>
            <option v-for="vol in volumes" :key="vol.id" :value="vol.id">
              Vol. {{ vol.number }} ({{ vol.year }})
            </option>
          </select>
        </div>

        <!-- Sort -->
        <div class="flex items-center gap-1.5">
          <ArrowUpDown :size="13" class="text-slate-400" />
          <select v-model="filters.sort" class="input-base h-9 w-auto py-1 text-xs" @change="filters.page = 1">
            <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </select>
        </div>

        <button
          v-if="hasActiveFilters"
          class="inline-flex items-center gap-1 rounded-lg bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-100 dark:bg-red-950/30 dark:text-red-400"
          @click="clearFilters"
        >
          <X :size="12" />{{ t('common.clear') }}
        </button>
      </div>
    </section>

    <!-- Error -->
    <div v-if="error" class="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 py-16 text-center dark:border-red-900/50 dark:bg-red-950/20">
      <AlertCircle :size="40" class="text-red-400" />
      <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4 text-sm" @click="fetchArticles">
        <RefreshCw :size="14" />{{ t('common.retry') }}
      </button>
    </div>

    <!-- Skeleton -->
    <div v-else-if="loading" class="flex flex-col gap-4">
      <div v-for="i in 5" :key="i" class="skeleton h-40 rounded-xl" />
    </div>

    <!-- Empty -->
    <div v-else-if="articles.length === 0" class="flex flex-col items-center justify-center rounded-xl border border-stone-200 bg-white py-24 dark:border-slate-700 dark:bg-slate-800">
      <svg class="h-24 w-24 text-slate-200 dark:text-slate-700" viewBox="0 0 120 120" fill="currentColor">
        <rect x="15" y="10" width="90" height="100" rx="10" opacity="0.4"/>
        <rect x="30" y="35" width="60" height="7" rx="3.5"/>
        <rect x="30" y="52" width="50" height="7" rx="3.5"/>
        <rect x="30" y="69" width="35" height="7" rx="3.5"/>
      </svg>
      <p class="mt-4 text-base font-medium text-slate-500 dark:text-slate-400">{{ t('articles.no_results') }}</p>
      <button v-if="hasActiveFilters" class="btn-ghost mt-3 text-sm" @click="clearFilters">{{ t('common.clear') }}</button>
    </div>

    <!-- Grouped by category (when no specific category filter active) -->
    <template v-else-if="showGrouped">
      <section v-for="section in grouped" :key="section.category?.id || 'uncat'" class="space-y-4">
        <div class="flex flex-wrap items-baseline gap-3 border-b-2 border-primary-400 pb-2">
          <h2 class="font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
            {{ section.category ? categoryName(section.category) : 'Boshqalar' }}
          </h2>
          <span class="text-xs font-medium text-slate-400">{{ section.items.length }} ta</span>
          <RouterLink
            v-if="section.category"
            :to="{ path: '/articles', query: { category: section.category.slug } }"
            class="ml-auto text-xs font-semibold text-primary-700 hover:text-primary-800 dark:text-primary-400"
          >
            {{ t('common.view_all') }} →
          </RouterLink>
        </div>
        <div class="flex flex-col gap-4">
          <ArticleCard
            v-for="article in section.items"
            :key="article.id"
            :article="article"
            :highlight-query="filters.search"
          />
        </div>
      </section>
    </template>

    <!-- Flat list (category filter active or single section) -->
    <div v-else class="flex flex-col gap-4">
      <ArticleCard
        v-for="article in articles"
        :key="article.id"
        :article="article"
        :highlight-query="filters.search"
      />
    </div>

    <!-- Pagination -->
    <div v-if="!loading && pages > 1" class="mt-8">
      <AppPagination :current-page="filters.page" :total-pages="pages" @change="onPageChange" />
    </div>
  </div>
</template>
