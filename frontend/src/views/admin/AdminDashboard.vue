<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import {
  FileText, Users, Download, BookOpen,
  Clock, Eye, CheckCircle, BookPlus,
  UserPlus, Megaphone, PenLine,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import StatsCard from '@/components/admin/StatsCard.vue'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'

const { t } = useI18n()
const router = useRouter()
const localeStore = useLocaleStore()

interface OverviewStats {
  total_articles: number
  published_this_month: number
  registered_users: number
  total_downloads: number
  pending_submissions: number
  under_review: number
  awaiting_decision: number
  published_change_pct: number
}

const stats = ref<OverviewStats | null>(null)
const monthly = ref<{ labels: string[]; data: number[] } | null>(null)
const topDownloads = ref<{ id: string; title: any; download_count: number }[]>([])
const recentSubmissions = ref<any[]>([])
const loadingStats = ref(true)

onMounted(async () => {
  try {
    const [overview, mon, top, recent] = await Promise.all([
      api.get<OverviewStats>('/api/admin/stats/overview'),
      api.get<{ labels: string[]; data: number[] }>('/api/admin/stats/monthly'),
      api.get<any[]>('/api/admin/stats/top-downloads'),
      api.get<any[]>('/api/admin/stats/recent-submissions'),
    ])
    stats.value = overview
    monthly.value = mon
    topDownloads.value = top
    recentSubmissions.value = recent
    await nextTick()
    renderChart(mon)
  } finally {
    loadingStats.value = false
  }
})

function renderChart(mon: { labels: string[]; data: number[] }) {
  const canvas = document.getElementById('monthlyChart') as HTMLCanvasElement | null
  if (!canvas) return
  // @ts-ignore
  if (typeof Chart === 'undefined') return
  // @ts-ignore
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: mon.labels,
      datasets: [{
        label: t('admin.dashboard.published'),
        data: mon.data,
        backgroundColor: 'rgba(79, 70, 229, 0.7)',
        borderColor: 'rgba(79, 70, 229, 1)',
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { stepSize: 1 },
          grid: { color: 'rgba(148, 163, 184, 0.15)' },
        },
        x: { grid: { display: false } },
      },
    },
  })
}

const quickActions = [
  { icon: BookPlus, label: 'admin.dashboard.createVolume', to: '/admin/volumes', color: 'bg-blue-50 text-blue-600 dark:bg-blue-950 dark:text-blue-400' },
  { icon: UserPlus, label: 'admin.dashboard.addEditorial', to: '/admin/editorial', color: 'bg-emerald-50 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400' },
  { icon: Megaphone, label: 'admin.dashboard.publishAnnouncement', to: '/admin/announcements', color: 'bg-amber-50 text-amber-600 dark:bg-amber-950 dark:text-amber-400' },
  { icon: PenLine, label: 'admin.dashboard.managePages', to: '/admin/pages', color: 'bg-purple-50 text-purple-600 dark:bg-purple-950 dark:text-purple-400' },
]
</script>

<template>
  <div>
    <h1 class="mb-6 font-serif text-2xl font-bold text-slate-900 dark:text-white">
      {{ t('admin.dashboard.title') }}
    </h1>

    <div v-if="loadingStats" class="flex justify-center py-24">
      <AppSpinner :size="36" class="text-primary-500" />
    </div>

    <template v-else-if="stats">
      <!-- Top 4 stats -->
      <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatsCard
          :label="t('admin.dashboard.total_articles')"
          :value="stats.total_articles"
          :icon="FileText"
          icon-bg="bg-blue-50 dark:bg-blue-950"
          icon-color="text-blue-600 dark:text-blue-400"
        />
        <StatsCard
          :label="t('admin.dashboard.publishedThisMonth')"
          :value="stats.published_this_month"
          :icon="CheckCircle"
          icon-bg="bg-emerald-50 dark:bg-emerald-950"
          icon-color="text-emerald-600 dark:text-emerald-400"
          :change="stats.published_change_pct"
          :change-label="t('admin.dashboard.vsLastMonth')"
        />
        <StatsCard
          :label="t('admin.dashboard.registeredUsers')"
          :value="stats.registered_users"
          :icon="Users"
          icon-bg="bg-violet-50 dark:bg-violet-950"
          icon-color="text-violet-600 dark:text-violet-400"
        />
        <StatsCard
          :label="t('admin.dashboard.totalDownloads')"
          :value="stats.total_downloads"
          :icon="Download"
          icon-bg="bg-amber-50 dark:bg-amber-950"
          icon-color="text-amber-600 dark:text-amber-400"
        />
      </div>

      <!-- Attention row -->
      <div class="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatsCard
          :label="t('admin.dashboard.pendingSubmissions')"
          :value="stats.pending_submissions"
          :icon="Clock"
          icon-bg="bg-amber-50 dark:bg-amber-950"
          icon-color="text-amber-600 dark:text-amber-400"
          :attention="stats.pending_submissions > 0"
        />
        <StatsCard
          :label="t('admin.dashboard.underReview')"
          :value="stats.under_review"
          :icon="Eye"
          icon-bg="bg-sky-50 dark:bg-sky-950"
          icon-color="text-sky-600 dark:text-sky-400"
          :attention="stats.under_review > 0"
        />
        <StatsCard
          :label="t('admin.dashboard.awaitingDecision')"
          :value="stats.awaiting_decision"
          :icon="BookOpen"
          icon-bg="bg-red-50 dark:bg-red-950"
          icon-color="text-red-600 dark:text-red-400"
          :attention="stats.awaiting_decision > 0"
        />
      </div>

      <!-- Chart + Top downloads -->
      <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Monthly chart -->
        <div class="col-span-2 rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('admin.dashboard.monthlyChart') }}
          </h2>
          <div class="h-52">
            <canvas id="monthlyChart" />
          </div>
        </div>

        <!-- Top downloads -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('admin.dashboard.topDownloads') }}
          </h2>
          <div class="flex flex-col gap-3">
            <div
              v-for="(article, idx) in topDownloads"
              :key="article.id"
              class="flex items-center gap-3"
            >
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-500 dark:bg-slate-700">
                {{ idx + 1 }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="line-clamp-1 text-sm text-slate-700 dark:text-slate-300">
                  {{ getLocalizedField(article.title, localeStore.current) || 'Sarlavhasiz' }}
                </p>
              </div>
              <div class="flex items-center gap-1 text-xs text-slate-500">
                <Download :size="12" />
                {{ article.download_count }}
              </div>
            </div>
            <p v-if="!topDownloads.length" class="text-sm text-slate-400">
              {{ t('common.no_data') }}
            </p>
          </div>
        </div>
      </div>

      <!-- Recent submissions + Quick actions -->
      <div class="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        <!-- Recent submissions -->
        <div class="col-span-2 rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-slate-700">
            <h2 class="text-sm font-semibold text-slate-700 dark:text-slate-300">
              {{ t('admin.dashboard.recentSubmissions') }}
            </h2>
            <RouterLink to="/admin/articles" class="text-xs text-primary-600 hover:underline dark:text-primary-400">
              {{ t('common.view_all') }}
            </RouterLink>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <tbody>
                <tr
                  v-for="article in recentSubmissions"
                  :key="article.id"
                  class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50"
                >
                  <td class="px-5 py-3">
                    <p class="line-clamp-1 font-medium text-slate-800 dark:text-slate-200">
                      {{ getLocalizedField(article.title, localeStore.current) || 'Sarlavhasiz' }}
                    </p>
                    <p class="text-xs text-slate-500">{{ article.author }}</p>
                  </td>
                  <td class="whitespace-nowrap px-4 py-3 text-xs text-slate-500">
                    {{ formatDateShort(article.created_at) }}
                  </td>
                  <td class="px-4 py-3">
                    <ArticleStatusBadge :status="article.status" />
                  </td>
                  <td class="px-4 py-3">
                    <RouterLink
                      :to="`/admin/articles/${article.id}/review`"
                      class="rounded-lg bg-primary-50 px-2.5 py-1 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300 dark:hover:bg-primary-950"
                    >
                      {{ t('review.manage_review') }}
                    </RouterLink>
                  </td>
                </tr>
                <tr v-if="!recentSubmissions.length">
                  <td colspan="4" class="px-5 py-8 text-center text-sm text-slate-400">
                    {{ t('common.no_data') }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Quick actions -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('admin.dashboard.quick_actions') }}
          </h2>
          <div class="grid grid-cols-2 gap-3">
            <RouterLink
              v-for="action in quickActions"
              :key="action.to"
              :to="action.to"
              class="flex flex-col items-center gap-2 rounded-xl border border-slate-200 p-3 text-center transition hover:shadow-sm dark:border-slate-700 hover:border-primary-200 dark:hover:border-primary-800"
            >
              <div class="flex h-10 w-10 items-center justify-center rounded-xl" :class="action.color.split(' ').slice(0, 2).join(' ')">
                <component :is="action.icon" :size="18" :class="action.color.split(' ').slice(2).join(' ')" />
              </div>
              <span class="text-xs font-medium leading-tight text-slate-600 dark:text-slate-300">
                {{ t(action.label) }}
              </span>
            </RouterLink>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
