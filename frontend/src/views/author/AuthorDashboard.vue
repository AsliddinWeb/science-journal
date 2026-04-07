<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  FilePlus, BookOpen, User, FileText, Clock, CheckCircle,
  XCircle, AlertCircle, RefreshCw, ExternalLink,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import { useLocaleStore } from '@/stores/locale'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'
import { formatDate } from '@/utils/formatDate'

interface Stats {
  total: number
  draft: number
  submitted: number
  under_review: number
  revision_required: number
  accepted: number
  rejected: number
  published: number
}

interface ArticleItem {
  id: string
  title: Record<string, string>
  status: string
  created_at: string
  updated_at: string
  submission_date?: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  pages: number
}

const { t, locale } = useI18n()
const router = useRouter()
const authStore = useAuthStore()
const localeStore = useLocaleStore()

const stats = ref<Stats | null>(null)
const articles = ref<ArticleItem[]>([])
const loading = ref(true)
const error = ref(false)

const user = computed(() => authStore.user)

function getTitle(article: ArticleItem): string {
  const titles = article.title
  return titles[localeStore.current] || titles.en || titles.ru || titles.uz || ''
}

const quickActions = computed(() => [
  {
    icon: FilePlus,
    label: t('author.dashboard.submit_new'),
    desc: t('author.dashboard.submit_new_desc'),
    to: { name: 'submit-article' },
    color: 'bg-primary-50 text-primary-600 dark:bg-primary-950 dark:text-primary-400',
  },
  {
    icon: BookOpen,
    label: t('author.dashboard.view_guidelines'),
    desc: t('author.dashboard.view_guidelines_desc'),
    to: { name: 'static-page', params: { slug: 'author-guidelines' } },
    color: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400',
  },
  {
    icon: User,
    label: t('author.dashboard.my_profile'),
    desc: t('author.dashboard.my_profile_desc'),
    to: { name: 'author-profile' },
    color: 'bg-violet-50 text-violet-600 dark:bg-violet-950 dark:text-violet-400',
  },
])

const statCards = computed(() => {
  if (!stats.value) return []
  return [
    {
      label: t('author.dashboard.stats_total'),
      value: stats.value.total,
      icon: FileText,
      color: 'text-primary-600 dark:text-primary-400',
      bg: 'bg-primary-50 dark:bg-primary-950',
    },
    {
      label: t('author.dashboard.stats_under_review'),
      value: (stats.value.submitted ?? 0) + (stats.value.under_review ?? 0),
      icon: Clock,
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-950',
    },
    {
      label: t('author.dashboard.stats_published'),
      value: stats.value.published,
      icon: CheckCircle,
      color: 'text-green-600 dark:text-green-400',
      bg: 'bg-green-50 dark:bg-green-950',
    },
    {
      label: t('author.dashboard.stats_rejected'),
      value: stats.value.rejected,
      icon: XCircle,
      color: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-50 dark:bg-red-950',
    },
  ]
})

async function load() {
  loading.value = true
  error.value = false
  try {
    const [statsData, articlesData] = await Promise.all([
      api.get<Stats>('/api/articles/my/stats'),
      api.get<PaginatedResponse<ArticleItem>>('/api/articles/my?limit=5'),
    ])
    stats.value = statsData
    articles.value = articlesData.items
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
    <!-- Header -->
    <div class="border-b border-slate-200 bg-slate-50 py-8 dark:border-slate-800 dark:bg-slate-900">
      <div class="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
              {{ t('author.dashboard.welcome', { name: user?.full_name ?? '' }) }}
            </h1>
            <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">{{ user?.email }}</p>
            <a
              v-if="user?.orcid_id"
              :href="`https://orcid.org/${user.orcid_id}`"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-1 inline-flex items-center gap-1.5 text-sm text-primary-600 hover:underline dark:text-primary-400"
            >
              <ExternalLink :size="13" />ORCID: {{ user.orcid_id }}
            </a>
          </div>
          <router-link :to="{ name: 'submit-article' }" class="btn-primary hidden sm:inline-flex">
            <FilePlus :size="16" />{{ t('author.dashboard.submit_new') }}
          </router-link>
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-5xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">

      <!-- Error -->
      <div v-if="error" class="flex flex-col items-center py-16">
        <AlertCircle :size="40" class="text-red-400" />
        <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
        <button class="btn-ghost mt-4" @click="load">
          <RefreshCw :size="15" />{{ t('common.retry') }}
        </button>
      </div>

      <template v-else>
        <!-- Stats skeleton -->
        <div v-if="loading" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div v-for="i in 4" :key="i" class="card animate-pulse p-5">
            <div class="mb-3 h-9 w-9 rounded-xl bg-slate-200 dark:bg-slate-700" />
            <div class="mb-1 h-7 w-10 rounded bg-slate-200 dark:bg-slate-700" />
            <div class="h-3 w-24 rounded bg-slate-100 dark:bg-slate-800" />
          </div>
        </div>

        <!-- Stats -->
        <div v-else-if="stats" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div v-for="card in statCards" :key="card.label" class="card p-5">
            <div :class="['mb-3 flex h-9 w-9 items-center justify-center rounded-xl', card.bg]">
              <component :is="card.icon" :size="18" :class="card.color" />
            </div>
            <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ card.value }}</p>
            <p class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{{ card.label }}</p>
          </div>
        </div>

        <!-- Recent submissions -->
        <div>
          <div class="mb-4 flex items-center justify-between">
            <h2 class="font-serif text-lg font-bold text-slate-900 dark:text-white">
              {{ t('author.dashboard.recent_submissions') }}
            </h2>
            <router-link :to="{ name: 'my-articles' }" class="text-sm text-primary-600 hover:underline dark:text-primary-400">
              {{ t('common.view_all') }}
            </router-link>
          </div>

          <!-- Table skeleton -->
          <div v-if="loading" class="card divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
            <div v-for="i in 3" :key="i" class="flex animate-pulse items-center gap-4 p-4">
              <div class="flex-1 space-y-2">
                <div class="h-4 w-3/4 rounded bg-slate-200 dark:bg-slate-700" />
                <div class="h-3 w-1/3 rounded bg-slate-100 dark:bg-slate-800" />
              </div>
              <div class="h-6 w-20 rounded-full bg-slate-200 dark:bg-slate-700" />
            </div>
          </div>

          <div v-else-if="articles.length === 0" class="card p-8 text-center text-sm text-slate-400">
            {{ t('author.dashboard.no_submissions') }}
          </div>

          <div v-else class="card overflow-hidden">
            <div class="divide-y divide-slate-100 dark:divide-slate-800">
              <div
                v-for="article in articles"
                :key="article.id"
                class="flex cursor-pointer items-center gap-4 p-4 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
                @click="router.push({ name: 'article-status', params: { id: article.id } })"
              >
                <div class="min-w-0 flex-1">
                  <p class="truncate text-sm font-medium text-slate-900 dark:text-white">
                    {{ getTitle(article) || t('author.dashboard.untitled') }}
                  </p>
                  <p class="mt-0.5 text-xs text-slate-400">
                    {{ formatDate(article.submission_date ?? article.created_at, locale) }}
                  </p>
                </div>
                <ArticleStatusBadge :status="(article.status as any)" size="sm" />
                <span class="shrink-0 text-sm text-primary-600 dark:text-primary-400">
                  {{ ['revision_required', 'draft'].includes(article.status) ? t('author.dashboard.action_revise') : t('author.dashboard.action_view') }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick actions -->
        <div>
          <h2 class="mb-4 font-serif text-lg font-bold text-slate-900 dark:text-white">
            {{ t('author.dashboard.quick_actions') }}
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <router-link
              v-for="action in quickActions"
              :key="action.label"
              :to="action.to"
              class="card group flex items-start gap-4 p-5 transition-colors hover:border-primary-200 dark:hover:border-primary-800"
            >
              <div :class="['flex h-10 w-10 shrink-0 items-center justify-center rounded-xl', action.color]">
                <component :is="action.icon" :size="20" />
              </div>
              <div>
                <p class="font-semibold text-slate-900 group-hover:text-primary-700 dark:text-white dark:group-hover:text-primary-400">
                  {{ action.label }}
                </p>
                <p class="mt-0.5 text-xs text-slate-400">{{ action.desc }}</p>
              </div>
            </router-link>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>
