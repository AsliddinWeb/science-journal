<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useApi } from '@/composables/useApi'
import { formatDateShort } from '@/utils/formatDate'
import { getLocalizedField } from '@/utils/truncate'
import { useLocaleStore } from '@/stores/locale'
import {
  InboxIcon, Clock, CheckCircle, XCircle, AlertTriangle, FileText, ChevronDown, ChevronUp,
} from 'lucide-vue-next'
import ReviewCard from '@/components/review/ReviewCard.vue'
import DeclineModal from '@/components/review/DeclineModal.vue'
import RecommendationBadge from '@/components/review/RecommendationBadge.vue'

interface ReviewItem {
  id: string
  article_id: string
  status: string
  recommendation: string | null
  deadline: string | null
  accepted_at: string | null
  submitted_at: string | null
  created_at: string
  article: { id: string; title: Record<string, string>; language: string } | null
}

const { t } = useI18n()
const api = useApi()
const localeStore = useLocaleStore()

const reviews = ref<ReviewItem[]>([])
const loading = ref(true)
const actionLoading = ref(false)
const declineModalReviewId = ref<string | null>(null)
const showCompleted = ref(false)

onMounted(async () => {
  await loadReviews()
})

async function loadReviews() {
  loading.value = true
  try {
    reviews.value = await api.get<ReviewItem[]>('/api/reviews/my')
  } finally {
    loading.value = false
  }
}

const pending = computed(() => reviews.value.filter(r => r.status === 'pending'))
const active = computed(() => reviews.value.filter(r => r.status === 'accepted'))
const completed = computed(() => reviews.value.filter(r => r.status === 'completed'))
const overdue = computed(() =>
  reviews.value.filter(r =>
    (r.status === 'pending' || r.status === 'accepted') &&
    r.deadline && new Date(r.deadline) < new Date()
  )
)

function articleTitle(r: ReviewItem) {
  return r.article
    ? getLocalizedField(r.article.title, localeStore.current) || `#${r.article_id.slice(0, 8)}`
    : `#${r.article_id.slice(0, 8)}`
}

function daysLeft(deadline: string | null): number | null {
  if (!deadline) return null
  return Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000)
}

function deadlineClass(deadline: string | null) {
  const d = daysLeft(deadline)
  if (d === null) return 'text-slate-400'
  if (d < 0) return 'text-red-600 font-semibold dark:text-red-400'
  if (d <= 3) return 'text-red-500 font-semibold dark:text-red-400'
  if (d <= 7) return 'text-amber-500 dark:text-amber-400'
  return 'text-green-600 dark:text-green-400'
}

async function handleAccept(reviewId: string) {
  actionLoading.value = true
  try {
    await api.post(`/api/reviews/${reviewId}/accept`, {})
    await loadReviews()
  } finally {
    actionLoading.value = false
  }
}

function openDecline(reviewId: string) {
  declineModalReviewId.value = reviewId
}

async function handleDeclineConfirm(reviewId: string, reason: string) {
  actionLoading.value = true
  try {
    await api.post(`/api/reviews/${reviewId}/decline`, { reason })
    declineModalReviewId.value = null
    await loadReviews()
  } finally {
    actionLoading.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-10 sm:px-6 lg:px-8">
    <h1 class="mb-8 font-serif text-2xl font-bold text-slate-900 dark:text-white">
      {{ t('review.dashboard_title') }}
    </h1>

    <!-- Stats row -->
    <div class="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-1 flex items-center gap-2 text-amber-500"><InboxIcon class="h-4 w-4" /><span class="text-xs font-medium">{{ t('review.pending_invitations') }}</span></div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ pending.length }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-1 flex items-center gap-2 text-blue-500"><Clock class="h-4 w-4" /><span class="text-xs font-medium">{{ t('review.active_reviews') }}</span></div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ active.length }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-1 flex items-center gap-2 text-green-500"><CheckCircle class="h-4 w-4" /><span class="text-xs font-medium">{{ t('review.completed_reviews') }}</span></div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ completed.length }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-1 flex items-center gap-2 text-red-500"><AlertTriangle class="h-4 w-4" /><span class="text-xs font-medium">{{ t('review.overdue') }}</span></div>
        <p class="text-2xl font-bold text-slate-900 dark:text-white">{{ overdue.length }}</p>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="h-28 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700" />
    </div>

    <template v-else>
      <!-- Pending Invitations -->
      <section class="mb-8">
        <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
          {{ t('review.pending_invitations') }}
          <span class="ml-2 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-bold text-amber-700 dark:bg-amber-900/30 dark:text-amber-400">{{ pending.length }}</span>
        </h2>
        <div v-if="pending.length === 0" class="rounded-xl border border-dashed border-slate-300 py-8 text-center text-sm text-slate-400 dark:border-slate-700">
          {{ t('review.no_pending') }}
        </div>
        <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <ReviewCard
            v-for="r in pending"
            :key="r.id"
            :review="r"
            :loading="actionLoading"
            @accept="handleAccept"
            @decline="openDecline"
          />
        </div>
      </section>

      <!-- Active Reviews -->
      <section class="mb-8">
        <h2 class="mb-4 text-lg font-semibold text-slate-900 dark:text-white">
          {{ t('review.active_reviews') }}
          <span class="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-bold text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">{{ active.length }}</span>
        </h2>
        <div v-if="active.length === 0" class="rounded-xl border border-dashed border-slate-300 py-8 text-center text-sm text-slate-400 dark:border-slate-700">
          {{ t('review.no_active') }}
        </div>
        <div v-else class="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 dark:bg-slate-800/60">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.article_title') }}</th>
                <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.assigned_date') }}</th>
                <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.deadline') }}</th>
                <th class="px-4 py-3 text-right font-semibold text-slate-600 dark:text-slate-300"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
              <tr
                v-for="r in active"
                :key="r.id"
                class="bg-white hover:bg-slate-50 dark:bg-slate-800 dark:hover:bg-slate-700/50"
              >
                <td class="max-w-xs px-4 py-3">
                  <p class="line-clamp-1 font-medium text-slate-900 dark:text-white">{{ articleTitle(r) }}</p>
                </td>
                <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ formatDateShort(r.accepted_at || r.created_at) }}</td>
                <td class="px-4 py-3">
                  <span :class="deadlineClass(r.deadline)">
                    {{ r.deadline ? formatDateShort(r.deadline) : '—' }}
                    <template v-if="r.deadline && daysLeft(r.deadline) !== null">
                      <span class="text-xs">
                        ({{ daysLeft(r.deadline)! < 0 ? t('review.overdue') : `${daysLeft(r.deadline)} ${t('review.daysLeft')}` }})
                      </span>
                    </template>
                  </span>
                </td>
                <td class="px-4 py-3 text-right">
                  <RouterLink
                    :to="`/reviewer/review/${r.id}`"
                    class="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700"
                  >
                    <FileText class="h-3.5 w-3.5" />
                    {{ t('review.write_review') }}
                  </RouterLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Completed Reviews (collapsible) -->
      <section>
        <button
          class="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-900 dark:text-white"
          @click="showCompleted = !showCompleted"
        >
          {{ t('review.completed_reviews') }}
          <span class="rounded-full bg-green-100 px-2 py-0.5 text-xs font-bold text-green-700 dark:bg-green-900/30 dark:text-green-400">{{ completed.length }}</span>
          <component :is="showCompleted ? ChevronUp : ChevronDown" class="h-4 w-4 text-slate-400" />
        </button>

        <Transition name="slide">
          <div v-if="showCompleted && completed.length > 0" class="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700">
            <table class="w-full text-sm">
              <thead class="bg-slate-50 dark:bg-slate-800/60">
                <tr>
                  <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.article_title') }}</th>
                  <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.submitted_date') }}</th>
                  <th class="px-4 py-3 text-left font-semibold text-slate-600 dark:text-slate-300">{{ t('review.recommendation_label') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                <tr
                  v-for="r in completed"
                  :key="r.id"
                  class="bg-white dark:bg-slate-800"
                >
                  <td class="max-w-xs px-4 py-3">
                    <p class="line-clamp-1 font-medium text-slate-900 dark:text-white">{{ articleTitle(r) }}</p>
                  </td>
                  <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ formatDateShort(r.submitted_at || r.created_at) }}</td>
                  <td class="px-4 py-3">
                    <RecommendationBadge :recommendation="r.recommendation" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </Transition>
      </section>
    </template>

    <!-- Decline modal -->
    <DeclineModal
      v-if="declineModalReviewId"
      :review-id="declineModalReviewId"
      :loading="actionLoading"
      @confirm="handleDeclineConfirm"
      @cancel="declineModalReviewId = null"
    />
  </div>
</template>

<style scoped>
.slide-enter-active, .slide-leave-active { transition: opacity 0.2s, max-height 0.25s; overflow: hidden; }
.slide-enter-from, .slide-leave-to { opacity: 0; max-height: 0; }
.slide-enter-to, .slide-leave-from { opacity: 1; max-height: 800px; }
</style>
