<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Eye, Pencil, Download, AlertCircle, RefreshCw } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import { formatDate } from '@/utils/formatDate'

interface ArticleItem {
  id: string
  title: Record<string, string>
  status: string
  created_at: string
  submission_date?: string | null
  category_id?: string | null
  reviews?: { id: string }[]
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pages: number
  limit: number
}

const { t, locale } = useI18n()
const router = useRouter()
const localeStore = useLocaleStore()

type StatusFilter = 'all' | 'draft' | 'submitted' | 'under_review' | 'revision_required' | 'accepted' | 'rejected' | 'published'

const statusFilter = ref<StatusFilter>('all')
const articles = ref<ArticleItem[]>([])
const total = ref(0)
const pages = ref(1)
const page = ref(1)
const loading = ref(true)
const error = ref(false)

const PAGE_SIZE = 15

const filterTabs: { key: StatusFilter; label: string }[] = [
  { key: 'all', label: t('common.all') },
  { key: 'draft', label: t('author.status.draft') },
  { key: 'submitted', label: t('author.status.submitted') },
  { key: 'under_review', label: t('author.status.under_review') },
  { key: 'revision_required', label: t('author.status.revision_required') },
  { key: 'published', label: t('author.status.published') },
  { key: 'rejected', label: t('author.status.rejected') },
]

function getTitle(article: ArticleItem): string {
  const titles = article.title
  return titles[localeStore.current] || titles.en || titles.ru || titles.uz || ''
}

async function load() {
  loading.value = true
  error.value = false
  try {
    const statusParam = statusFilter.value !== 'all' ? `&status=${statusFilter.value}` : ''
    const data = await api.get<PaginatedResponse<ArticleItem>>(
      `/api/articles/my?page=${page.value}&limit=${PAGE_SIZE}${statusParam}`
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

watch(statusFilter, () => { page.value = 1; load() })
onMounted(load)

function onPageChange(p: number) {
  page.value = p
  load()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function canEdit(status: string) {
  return ['draft', 'revision_required'].includes(status)
}
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <!-- Header -->
    <div class="border-b border-slate-200 bg-slate-50 py-8 dark:border-slate-800 dark:bg-slate-900">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('author.myArticles.title') }}
        </h1>
      </div>
    </div>

    <!-- Filter tabs -->
    <div class="border-b border-slate-200 dark:border-slate-800">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="flex gap-1 overflow-x-auto py-3 scrollbar-hide">
          <button
            v-for="tab in filterTabs"
            :key="tab.key"
            class="shrink-0 rounded-lg px-3 py-1.5 text-sm font-medium transition-colors"
            :class="statusFilter === tab.key
              ? 'bg-primary-100 text-primary-700 dark:bg-primary-950 dark:text-primary-400'
              : 'text-slate-500 hover:bg-slate-100 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800'"
            @click="statusFilter = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-5xl px-4 py-6 sm:px-6 lg:px-8">

      <!-- Error -->
      <div v-if="error" class="flex flex-col items-center py-16">
        <AlertCircle :size="40" class="text-red-400" />
        <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
        <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
      </div>

      <!-- Skeleton -->
      <div v-else-if="loading" class="card overflow-hidden divide-y divide-slate-100 dark:divide-slate-800">
        <div v-for="i in 5" :key="i" class="flex animate-pulse items-center gap-4 p-4">
          <div class="flex-1 space-y-2">
            <div class="h-4 w-2/3 rounded bg-slate-200 dark:bg-slate-700" />
            <div class="h-3 w-1/4 rounded bg-slate-100 dark:bg-slate-800" />
          </div>
          <div class="h-6 w-24 rounded-full bg-slate-200 dark:bg-slate-700" />
          <div class="h-7 w-20 rounded-lg bg-slate-100 dark:bg-slate-800" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="articles.length === 0" class="flex flex-col items-center py-20 text-slate-400">
        <p>{{ t('author.myArticles.empty') }}</p>
      </div>

      <!-- Table -->
      <div v-else>
        <!-- Desktop table -->
        <div class="card hidden overflow-hidden sm:block">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs uppercase tracking-wider text-slate-500 dark:bg-slate-800/50 dark:text-slate-400">
              <tr>
                <th class="px-4 py-3 text-left">{{ t('author.myArticles.col_title') }}</th>
                <th class="px-4 py-3 text-left">{{ t('author.myArticles.col_date') }}</th>
                <th class="px-4 py-3 text-left">{{ t('author.myArticles.col_status') }}</th>
                <th class="px-4 py-3 text-left">{{ t('author.myArticles.col_reviews') }}</th>
                <th class="px-4 py-3 text-right">{{ t('author.myArticles.col_actions') }}</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr
                v-for="article in articles"
                :key="article.id"
                class="cursor-pointer transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
                @click="router.push({ name: 'article-status', params: { id: article.id } })"
              >
                <td class="max-w-[280px] px-4 py-3">
                  <p class="truncate font-medium text-slate-900 dark:text-white">{{ getTitle(article) }}</p>
                </td>
                <td class="whitespace-nowrap px-4 py-3 text-slate-400">
                  {{ formatDate(article.submission_date ?? article.created_at, locale) }}
                </td>
                <td class="px-4 py-3">
                  <ArticleStatusBadge :status="(article.status as any)" />
                </td>
                <td class="px-4 py-3 text-slate-500">
                  {{ article.reviews?.length ?? 0 }}
                </td>
                <td class="px-4 py-3 text-right">
                  <div class="flex justify-end gap-1" @click.stop>
                    <router-link
                      :to="{ name: 'article-status', params: { id: article.id } }"
                      class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-700 dark:hover:text-white"
                      :title="t('common.edit')"
                    >
                      <Eye :size="16" />
                    </router-link>
                    <a
                      v-if="article.status === 'published'"
                      :href="`/api/articles/${article.id}/download`"
                      class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 hover:text-green-600 dark:hover:bg-slate-700"
                      :title="t('articles.download_pdf')"
                    >
                      <Download :size="16" />
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Mobile cards -->
        <div class="flex flex-col gap-3 sm:hidden">
          <div
            v-for="article in articles"
            :key="article.id"
            class="card cursor-pointer p-4"
            @click="router.push({ name: 'article-status', params: { id: article.id } })"
          >
            <div class="mb-2 flex items-start justify-between gap-3">
              <p class="line-clamp-2 text-sm font-medium text-slate-900 dark:text-white">{{ getTitle(article) }}</p>
              <ArticleStatusBadge :status="(article.status as any)" size="sm" />
            </div>
            <p class="text-xs text-slate-400">{{ formatDate(article.submission_date ?? article.created_at, locale) }}</p>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="pages > 1" class="mt-6">
          <AppPagination :current-page="page" :total-pages="pages" @change="onPageChange" />
        </div>
      </div>
    </div>
  </div>
</template>
