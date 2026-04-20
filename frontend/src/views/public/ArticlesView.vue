<script setup lang="ts">
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { SlidersHorizontal, X, Search as SearchIcon, AlertCircle, RefreshCw, Globe, BookOpen as BookOpenIcon, Calendar as CalendarIcon, ArrowUpDown } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import type { Article, PaginatedResponse } from '@/types/article'
import type { Volume } from '@/types/volume'
import ArticleCard from '@/components/article/ArticleCard.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import SkeletonText from '@/components/ui/SkeletonText.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()

useSeoMeta({
  title: t('nav.articles'),
  description: 'Browse all published scientific articles. Filter by language, volume and category.',
  canonical: 'https://scientists.uz/articles',
  ogUrl: 'https://scientists.uz/articles',
})
const route = useRoute()
const router = useRouter()

const articles = ref<Article[]>([])
const volumes = ref<Volume[]>([])
const total = ref(0)
const pages = ref(1)
const loading = ref(false)
const error = ref(false)
const sidebarOpen = ref(false)

const filters = reactive({
  search: (route.query.q as string) ?? '',
  language: (route.query.language as string) ?? '',
  volume_id: (route.query.volume as string) ?? '',
  year: (route.query.year as string) ?? '',
  sort: (route.query.sort as string) ?? 'newest',
  page: Number(route.query.page) || 1,
})

const PAGE_SIZE = 10

const sortOptions = computed(() => [
  { value: 'newest', label: t('articles.sort_newest') },
  { value: 'oldest', label: t('articles.sort_oldest') },
  { value: 'downloads', label: t('articles.sort_downloads') },
])

const hasActiveFilters = computed(() =>
  !!(filters.search || filters.language || filters.volume_id || filters.year || filters.sort !== 'newest')
)

const yearOptions = computed(() => {
  const years = [...new Set(volumes.value.map((v) => v.year))].sort((a, b) => b - a)
  return years
})

async function fetchArticles() {
  loading.value = true
  error.value = false
  try {
    const params = new URLSearchParams()
    params.set('page', String(filters.page))
    params.set('limit', String(PAGE_SIZE))
    params.set('status', 'published')
    if (filters.search) params.set('search', filters.search)
    if (filters.language) params.set('language', filters.language)
    if (filters.volume_id) params.set('volume_id', filters.volume_id)
    if (filters.year) params.set('year', filters.year)
    if (filters.sort === 'oldest') params.set('sort', 'published_date_asc')
    else if (filters.sort === 'downloads') params.set('sort', 'download_count_desc')
    else params.set('sort', 'published_date_desc')

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
  try {
    volumes.value = await api.get<Volume[]>('/api/volumes')
  } catch {}
}

onMounted(() => { fetchVolumes(); fetchArticles() })

watch(
  () => ({ ...filters }),
  () => {
    router.replace({
      query: {
        ...(filters.search && { q: filters.search }),
        ...(filters.language && { language: filters.language }),
        ...(filters.volume_id && { volume: filters.volume_id }),
        ...(filters.year && { year: filters.year }),
        ...(filters.sort !== 'newest' && { sort: filters.sort }),
        ...(filters.page > 1 && { page: String(filters.page) }),
      },
    })
    fetchArticles()
  },
  { deep: true }
)

function clearFilters() {
  filters.search = ''
  filters.language = ''
  filters.volume_id = ''
  filters.year = ''
  filters.sort = 'newest'
  filters.page = 1
}

function onSearchInput(e: Event) {
  filters.search = (e.target as HTMLInputElement).value
  filters.page = 1
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

    <div>
      <div class="flex gap-6">

        <!-- Mobile sidebar backdrop -->
        <Transition enter-active-class="transition-opacity duration-200" enter-from-class="opacity-0" leave-active-class="transition-opacity duration-150" leave-to-class="opacity-0">
          <div v-if="sidebarOpen" class="fixed inset-0 z-40 bg-black/50 lg:hidden" @click="sidebarOpen = false" />
        </Transition>

        <!-- Sidebar -->
        <aside
          class="fixed left-0 top-0 z-50 h-full w-72 overflow-y-auto bg-white p-5 shadow-xl transition-transform duration-300 dark:bg-slate-900 lg:static lg:z-auto lg:h-auto lg:w-60 lg:shrink-0 lg:translate-x-0 lg:overflow-visible lg:p-0 lg:shadow-none"
          :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
        >
          <!-- Mobile header -->
          <div class="mb-5 flex items-center justify-between lg:hidden">
            <span class="font-semibold text-slate-900 dark:text-white">{{ t('common.filter') }}</span>
            <button class="rounded-lg p-1 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800" @click="sidebarOpen = false">
              <X :size="18" />
            </button>
          </div>

          <div class="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
            <!-- Header -->
            <div class="flex items-center gap-2 bg-journal-900 px-4 py-3 text-primary-300">
              <SlidersHorizontal :size="14" />
              <h3 class="font-serif text-xs font-bold uppercase tracking-wider">{{ t('common.filter') }}</h3>
              <button
                v-if="hasActiveFilters"
                class="ml-auto flex h-5 w-5 items-center justify-center rounded-full bg-primary-500/20 text-[10px] font-bold text-primary-300 hover:bg-primary-500/30"
                :title="t('common.clear')"
                @click="clearFilters"
              >
                ×
              </button>
            </div>

            <div class="divide-y divide-stone-100 dark:divide-slate-700">
              <!-- Language filter -->
              <div class="px-4 py-4">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">
                  <Globe :size="11" />
                  {{ t('articles.filter_language') }}
                </p>
                <div class="flex flex-col gap-1">
                  <button
                    v-for="lang in langOptions"
                    :key="lang.value"
                    class="flex items-center justify-between rounded-md px-3 py-1.5 text-left text-xs font-medium transition"
                    :class="filters.language === lang.value
                      ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                      : 'text-slate-600 hover:bg-stone-50 dark:text-slate-400 dark:hover:bg-slate-700'"
                    @click="() => { filters.language = lang.value; filters.page = 1 }"
                  >
                    <span>{{ lang.label() }}</span>
                    <span v-if="filters.language === lang.value" class="text-primary-600 dark:text-primary-400">✓</span>
                  </button>
                </div>
              </div>

              <!-- Volume filter -->
              <div class="px-4 py-4">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">
                  <BookOpenIcon :size="11" />
                  {{ t('articles.filter_volume') }}
                </p>
                <select v-model="filters.volume_id" class="input-base text-xs" @change="filters.page = 1">
                  <option value="">{{ t('common.all') }}</option>
                  <option v-for="vol in volumes" :key="vol.id" :value="vol.id">
                    Vol. {{ vol.number }} ({{ vol.year }})
                  </option>
                </select>
              </div>

              <!-- Year filter -->
              <div class="px-4 py-4">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">
                  <CalendarIcon :size="11" />
                  {{ t('articles.filter_year') }}
                </p>
                <div class="flex flex-wrap gap-1">
                  <button
                    class="rounded-md px-2 py-1 text-xs font-medium transition"
                    :class="!filters.year
                      ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                      : 'bg-stone-100 text-slate-600 hover:bg-stone-200 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-slate-600'"
                    @click="() => { filters.year = ''; filters.page = 1 }"
                  >{{ t('common.all') }}</button>
                  <button
                    v-for="y in yearOptions"
                    :key="y"
                    class="rounded-md px-2 py-1 text-xs font-medium transition"
                    :class="filters.year === String(y)
                      ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                      : 'bg-stone-100 text-slate-600 hover:bg-stone-200 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-slate-600'"
                    @click="() => { filters.year = String(y); filters.page = 1 }"
                  >{{ y }}</button>
                </div>
              </div>

              <!-- Sort -->
              <div class="px-4 py-4">
                <p class="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">
                  <ArrowUpDown :size="11" />
                  {{ t('articles.sort_label') }}
                </p>
                <select v-model="filters.sort" class="input-base text-xs" @change="filters.page = 1">
                  <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
                </select>
              </div>
            </div>

            <!-- Clear button -->
            <div v-if="hasActiveFilters" class="border-t border-stone-200 px-4 py-3 dark:border-slate-700">
              <button
                class="flex w-full items-center justify-center gap-1.5 rounded-lg bg-red-50 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-100 dark:bg-red-950/30 dark:text-red-400 dark:hover:bg-red-950/50"
                @click="clearFilters"
              >
                <X :size="12" />
                {{ t('common.clear') }}
              </button>
            </div>
          </div>
        </aside>

        <!-- Main -->
        <div class="min-w-0 flex-1">
          <!-- Search bar + mobile filter toggle -->
          <div class="mb-6 flex gap-3">
            <div class="relative flex-1">
              <SearchIcon :size="17" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
              <input
                type="search"
                :value="filters.search"
                :placeholder="t('articles.search_placeholder')"
                class="input-base pl-9"
                @input="onSearchInput"
              />
            </div>
            <button
              class="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700 lg:hidden"
              @click="sidebarOpen = true"
            >
              <SlidersHorizontal :size="16" />
              {{ t('common.filter') }}
              <span v-if="hasActiveFilters" class="flex h-4 w-4 items-center justify-center rounded-full bg-primary-600 text-xs font-bold text-white">!</span>
            </button>
          </div>

          <!-- Error -->
          <div v-if="error" class="flex flex-col items-center justify-center rounded-xl border border-red-200 bg-red-50 py-16 text-center dark:border-red-900/50 dark:bg-red-950/20">
            <AlertCircle :size="40" class="text-red-400" />
            <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
            <button class="btn-ghost mt-4 text-sm" @click="fetchArticles">
              <RefreshCw :size="14" />
              {{ t('common.retry') }}
            </button>
          </div>

          <!-- Skeleton -->
          <div v-else-if="loading" class="flex flex-col gap-4">
            <div v-for="i in 5" :key="i" class="card animate-pulse p-5">
              <div class="flex gap-2 mb-3">
                <div class="h-5 w-12 rounded-full bg-slate-200 dark:bg-slate-700" />
                <div class="h-5 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
              </div>
              <div class="h-6 w-3/4 rounded-lg bg-slate-200 dark:bg-slate-700 mb-2" />
              <div class="h-4 w-1/3 rounded bg-slate-100 dark:bg-slate-800 mb-4" />
              <div class="space-y-2">
                <div class="h-3 rounded bg-slate-100 dark:bg-slate-800" />
                <div class="h-3 rounded bg-slate-100 dark:bg-slate-800" />
                <div class="h-3 w-2/3 rounded bg-slate-100 dark:bg-slate-800" />
              </div>
            </div>
          </div>

          <!-- Empty state -->
          <div v-else-if="articles.length === 0" class="flex flex-col items-center justify-center py-24">
            <svg class="h-28 w-28 text-slate-200 dark:text-slate-800" viewBox="0 0 120 120" fill="currentColor">
              <rect x="15" y="10" width="90" height="100" rx="10" fill="currentColor" opacity="0.4"/>
              <rect x="30" y="35" width="60" height="7" rx="3.5" fill="currentColor"/>
              <rect x="30" y="52" width="50" height="7" rx="3.5" fill="currentColor"/>
              <rect x="30" y="69" width="35" height="7" rx="3.5" fill="currentColor"/>
            </svg>
            <p class="mt-4 text-base font-medium text-slate-500 dark:text-slate-400">{{ t('articles.no_results') }}</p>
            <button v-if="hasActiveFilters" class="btn-ghost mt-3 text-sm" @click="clearFilters">
              {{ t('common.clear') }}
            </button>
          </div>

          <!-- Articles -->
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
      </div>
    </div>
  </div>
</template>
