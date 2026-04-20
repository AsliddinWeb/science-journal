<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BookOpen, Calendar, FileText, ChevronRight, AlertCircle, RefreshCw } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import type { Article, PaginatedResponse } from '@/types/article'
import type { Issue, Volume } from '@/types/volume'
import { formatDate } from '@/utils/formatDate'
import ArticleCard from '@/components/article/ArticleCard.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()
const route = useRoute()

const { apply: applySeo } = useSeoMeta()

const volumeId = computed(() => route.params.volumeId as string)
const issueId = computed(() => route.params.issueId as string)

const volume = ref<Volume | null>(null)
const issue = ref<Issue | null>(null)
const articles = ref<Article[]>([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const loading = ref(true)
const error = ref(false)

const PAGE_SIZE = 15

async function load() {
  loading.value = true
  error.value = false
  try {
    const [volumeData, articlesData] = await Promise.all([
      api.get<Volume>(`/api/volumes/${volumeId.value}`),
      api.get<PaginatedResponse<Article>>(
        `/api/articles?issue_id=${issueId.value}&page=${page.value}&limit=${PAGE_SIZE}&status=published`
      ),
    ])
    volume.value = volumeData
    issue.value = volumeData.issues.find((i) => i.id === issueId.value) ?? null
    articles.value = articlesData.items
    total.value = articlesData.total
    pages.value = articlesData.pages
    if (volumeData && issue.value) {
      applySeo({
        title: `Vol. ${volumeData.number}, Issue ${issue.value.number} (${volumeData.year})`,
        description: `Browse articles in Volume ${volumeData.number}, Issue ${issue.value.number} of Science and Innovation Journal.`,
        ogUrl: `https://scientists.uz/archive/${volumeData.id}/issues/${issue.value.id}`,
        canonical: `https://scientists.uz/archive/${volumeData.id}/issues/${issue.value.id}`,
      })
    }
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

function onPageChange(p: number) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
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
      <div class="relative overflow-hidden border-b border-slate-200 bg-gradient-to-br from-slate-900 via-primary-950 to-slate-900 py-8">
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
          <div v-if="loading" class="animate-pulse space-y-3">
            <div class="h-4 w-64 rounded bg-slate-200 dark:bg-slate-700" />
            <div class="h-8 w-80 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div class="h-4 w-48 rounded bg-slate-100 dark:bg-slate-800" />
          </div>

          <!-- Issue info -->
          <div v-else-if="volume && issue" class="flex items-start gap-4">
            <div class="hidden h-16 w-16 items-center justify-center rounded-xl bg-white/10 backdrop-blur sm:flex">
              <BookOpen :size="28" class="text-primary-300" />
            </div>
            <div>
              <h1 class="font-serif text-3xl font-bold text-white">
                Vol. {{ volume.number }}, {{ t('archive.issue_label', { number: issue.number }) }}
              </h1>
              <div class="mt-2 flex flex-wrap items-center gap-4 text-sm text-slate-300">
                <span v-if="issue.published_date" class="flex items-center gap-1.5">
                  <Calendar :size="14" />
                  {{ formatDate(issue.published_date) }}
                </span>
                <span class="flex items-center gap-1.5">
                  <FileText :size="14" />
                  {{ total }} {{ t('archive.articles') }}
                </span>
              </div>
              <p v-if="issue.description" class="mt-2 text-sm text-slate-300">
                {{ issue.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Articles -->
      <div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">

        <!-- Skeleton -->
        <div v-if="loading" class="flex flex-col gap-4">
          <div v-for="i in 5" :key="i" class="card animate-pulse p-5">
            <div class="mb-3 flex gap-2">
              <div class="h-5 w-12 rounded-full bg-slate-200 dark:bg-slate-700" />
            </div>
            <div class="h-6 w-3/4 rounded-lg bg-slate-200 dark:bg-slate-700 mb-2" />
            <div class="h-4 w-1/3 rounded bg-slate-100 dark:bg-slate-800" />
          </div>
        </div>

        <!-- Empty -->
        <div v-else-if="articles.length === 0" class="flex flex-col items-center py-20">
          <FileText :size="48" class="text-slate-200 dark:text-slate-700" />
          <p class="mt-4 text-slate-400">{{ t('archive.no_articles_in_issue') }}</p>
        </div>

        <!-- List -->
        <div v-else class="flex flex-col gap-4">
          <ArticleCard
            v-for="article in articles"
            :key="article.id"
            :article="article"
          />
        </div>

        <!-- Pagination -->
        <div v-if="!loading && pages > 1" class="mt-8">
          <AppPagination :current-page="page" :total-pages="pages" @change="onPageChange" />
        </div>
      </div>
    </template>
  </div>
</template>
