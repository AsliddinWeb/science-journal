<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Search as SearchIcon, AlertCircle, RefreshCw, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import type { Article, PaginatedResponse } from '@/types/article'
import ArticleCard from '@/components/article/ArticleCard.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const query = ref((route.query.q as string) ?? '')

const { apply: applySeo } = useSeoMeta({ title: 'Search' })
watch(query, (q) => {
  applySeo({ title: q ? `${t('common.search')}: ${q}` : t('common.search') })
})
const inputValue = ref(query.value)
const articles = ref<Article[]>([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const loading = ref(false)
const error = ref(false)

const PAGE_SIZE = 10

async function search() {
  if (!query.value.trim()) {
    articles.value = []
    total.value = 0
    pages.value = 1
    return
  }
  loading.value = true
  error.value = false
  try {
    const data = await api.get<PaginatedResponse<Article>>(
      `/api/articles?search=${encodeURIComponent(query.value)}&page=${page.value}&limit=${PAGE_SIZE}&status=published`
    )
    articles.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function onSubmit() {
  query.value = inputValue.value.trim()
  page.value = 1
  router.replace({ query: query.value ? { q: query.value } : {} })
}

function clearSearch() {
  inputValue.value = ''
  query.value = ''
  page.value = 1
  articles.value = []
  total.value = 0
  router.replace({ query: {} })
}

function onPageChange(p: number) {
  page.value = p
  search()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// Run search on load and when URL query changes
onMounted(() => {
  if (query.value) search()
})
watch(() => route.query.q, (q) => {
  if (typeof q === 'string') {
    query.value = q
    inputValue.value = q
    page.value = 1
    search()
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Search header -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('search.title') }}</h1>
      <p class="mt-1 text-sm text-slate-300">{{ t('search.placeholder') }}</p>
      <form @submit.prevent="onSubmit" class="mt-5 flex gap-3">
        <div class="relative flex-1">
          <SearchIcon :size="18" class="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
          <input
            v-model="inputValue"
            type="search"
            :placeholder="t('search.placeholder')"
            class="input-base py-3 pl-11 pr-10 text-base"
            autofocus
          />
          <button
            v-if="inputValue"
            type="button"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            @click="clearSearch"
          >
            <X :size="16" />
          </button>
        </div>
        <button type="submit" class="btn-primary px-5">
          {{ t('search.search_btn') }}
        </button>
      </form>
    </section>

    <div>

      <!-- Results header -->
      <div v-if="query && !loading && !error" class="mb-6">
        <p class="text-sm text-slate-500 dark:text-slate-400">
          <span class="font-semibold text-slate-900 dark:text-white">{{ total.toLocaleString() }}</span>
          {{ t('search.results_for') }}
          <span class="font-semibold text-primary-700 dark:text-primary-400">"{{ query }}"</span>
        </p>
      </div>

      <!-- Error -->
      <div v-if="error" class="flex flex-col items-center py-16">
        <AlertCircle :size="40" class="text-red-400" />
        <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
        <button class="btn-ghost mt-4" @click="search"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
      </div>

      <!-- Loading skeletons -->
      <div v-else-if="loading" class="flex flex-col gap-4">
        <div v-for="i in 5" :key="i" class="card animate-pulse p-5">
          <div class="mb-3 flex gap-2">
            <div class="h-5 w-12 rounded-full bg-slate-200 dark:bg-slate-700" />
          </div>
          <div class="h-6 w-3/4 rounded-lg bg-slate-200 dark:bg-slate-700 mb-2" />
          <div class="h-4 w-1/3 rounded bg-slate-100 dark:bg-slate-800 mb-4" />
          <div class="space-y-2">
            <div class="h-3 rounded bg-slate-100 dark:bg-slate-800" />
            <div class="h-3 w-4/5 rounded bg-slate-100 dark:bg-slate-800" />
          </div>
        </div>
      </div>

      <!-- Empty: no query yet -->
      <div v-else-if="!query" class="flex flex-col items-center py-24 text-center">
        <svg class="h-28 w-28 text-slate-200 dark:text-slate-800" viewBox="0 0 120 120" fill="none" stroke="currentColor" stroke-width="3">
          <circle cx="50" cy="50" r="30" />
          <line x1="72" y1="72" x2="95" y2="95" stroke-linecap="round" />
        </svg>
        <p class="mt-5 font-medium text-slate-400">{{ t('search.start_searching') }}</p>
      </div>

      <!-- Empty: no results -->
      <div v-else-if="articles.length === 0" class="flex flex-col items-center py-24 text-center">
        <svg class="h-28 w-28 text-slate-200 dark:text-slate-800" viewBox="0 0 120 120" fill="currentColor">
          <rect x="15" y="10" width="90" height="100" rx="10" opacity="0.3"/>
          <rect x="30" y="40" width="60" height="7" rx="3.5"/>
          <rect x="30" y="57" width="45" height="7" rx="3.5"/>
          <circle cx="90" cy="85" r="22" fill="white" class="dark:fill-slate-950"/>
          <circle cx="90" cy="85" r="18" opacity="0.15"/>
          <line x1="83" y1="85" x2="97" y2="85" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          <line x1="90" y1="78" x2="90" y2="92" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <p class="mt-4 text-base font-medium text-slate-500 dark:text-slate-400">
          {{ t('search.no_results', { query }) }}
        </p>
        <p class="mt-2 text-sm text-slate-400">{{ t('search.try_different') }}</p>
      </div>

      <!-- Results -->
      <div v-else class="flex flex-col gap-4">
        <ArticleCard
          v-for="article in articles"
          :key="article.id"
          :article="article"
          :highlight-query="query"
        />
      </div>

      <!-- Pagination -->
      <div v-if="!loading && pages > 1" class="mt-8">
        <AppPagination :current-page="page" :total-pages="pages" @change="onPageChange" />
      </div>
    </div>
  </div>
</template>
