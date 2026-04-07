<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useApi } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import {
  ChevronLeft, UserPlus, Send, CheckCircle, XCircle,
  Clock, AlertCircle, Eye, ChevronDown, ChevronUp,
} from 'lucide-vue-next'
import ReviewerSearchDropdown from '@/components/review/ReviewerSearchDropdown.vue'
import RecommendationBadge from '@/components/review/RecommendationBadge.vue'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'

interface Reviewer {
  id: string
  full_name: string
  email: string
  affiliation: string | null
  avatar_url: string | null
}

interface ReviewRow {
  id: string
  reviewer_id: string
  status: string
  recommendation: string | null
  deadline: string | null
  submitted_at: string | null
  accepted_at: string | null
  declined_at: string | null
  invitation_sent_at: string | null
  editor_comments: string | null
  comments_to_author: string | null
  comments_to_editor: string | null
  decline_reason: string | null
  created_at: string
  reviewer: Reviewer | null
}

interface ArticleDetail {
  id: string
  title: Record<string, string>
  abstract: Record<string, string>
  status: string
  language: string
  submission_date: string | null
  author: { id: string; full_name: string; email: string } | null
  category_id: string | null
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()
const localeStore = useLocaleStore()

const articleId = computed(() => route.params.id as string)
const article = ref<ArticleDetail | null>(null)
const reviews = ref<ReviewRow[]>([])
const loading = ref(true)
const assigning = ref(false)
const deciding = ref(false)

// Assign form
const selectedReviewer = ref<Reviewer | null>(null)
const deadline = ref('')
const editorNote = ref('')
const shortDeadlineWarning = computed(() => {
  if (!deadline.value) return false
  const days = Math.ceil((new Date(deadline.value).getTime() - Date.now()) / 86400000)
  return days < 7
})

// Default deadline: today + 14 days
const defaultDeadline = new Date(Date.now() + 14 * 86400000).toISOString().split('T')[0]

// Decision form
const decision = ref('')
const decisionComments = ref('')
const expandedReview = ref<string | null>(null)

const hasCompletedReviews = computed(() => reviews.value.some(r => r.status === 'completed'))
const activeReviews = computed(() => reviews.value.filter(r => r.status !== 'declined'))

onMounted(async () => {
  deadline.value = defaultDeadline
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const [art, revs] = await Promise.all([
      api.get<ArticleDetail>(`/api/articles/${articleId.value}`),
      api.get<ReviewRow[]>(`/api/articles/${articleId.value}/reviews`),
    ])
    article.value = art
    reviews.value = revs
  } catch {
    toast.error(t('common.error'))
  } finally {
    loading.value = false
  }
}

const articleTitle = computed(() =>
  article.value ? getLocalizedField(article.value.title, localeStore.current) || t('common.untitled') : ''
)

const decisionOptions = [
  { value: 'accept', label: 'decision.accept', color: 'green' },
  { value: 'minor_revision', label: 'decision.minor_revision', color: 'blue' },
  { value: 'major_revision', label: 'decision.major_revision', color: 'amber' },
  { value: 'reject', label: 'decision.reject', color: 'red' },
]

const decisionCardClass = (value: string) => {
  const sel = decision.value === value
  const base = 'cursor-pointer rounded-xl border-2 px-4 py-3 text-sm font-medium transition-all'
  if (!sel) return `${base} border-slate-200 text-slate-600 hover:border-slate-300 dark:border-slate-700 dark:text-slate-400`
  const colors: Record<string, string> = {
    accept: 'border-green-500 bg-green-50 text-green-800 dark:border-green-600 dark:bg-green-900/20 dark:text-green-300',
    minor_revision: 'border-blue-500 bg-blue-50 text-blue-800 dark:border-blue-600 dark:bg-blue-900/20 dark:text-blue-300',
    major_revision: 'border-amber-500 bg-amber-50 text-amber-800 dark:border-amber-600 dark:bg-amber-900/20 dark:text-amber-300',
    reject: 'border-red-500 bg-red-50 text-red-800 dark:border-red-600 dark:bg-red-900/20 dark:text-red-300',
  }
  return `${base} ${colors[value] ?? ''}`
}

function statusIcon(status: string) {
  switch (status) {
    case 'accepted': return CheckCircle
    case 'completed': return CheckCircle
    case 'declined': return XCircle
    default: return Clock
  }
}

function statusIconClass(status: string) {
  switch (status) {
    case 'accepted': return 'text-blue-500'
    case 'completed': return 'text-green-500'
    case 'declined': return 'text-red-400'
    default: return 'text-amber-400'
  }
}

function initials(name: string) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function daysLeft(deadline: string | null) {
  if (!deadline) return null
  return Math.ceil((new Date(deadline).getTime() - Date.now()) / 86400000)
}

function deadlineClass(deadline: string | null) {
  const d = daysLeft(deadline)
  if (d === null) return 'text-slate-400'
  if (d < 0) return 'text-red-600 dark:text-red-400 font-semibold'
  if (d <= 3) return 'text-red-500 dark:text-red-400'
  if (d <= 7) return 'text-amber-500 dark:text-amber-400'
  return 'text-slate-600 dark:text-slate-300'
}

async function assignReviewer() {
  if (!selectedReviewer.value) return
  assigning.value = true
  try {
    await api.post(`/api/reviews/${articleId.value}/assign`, {
      reviewer_id: selectedReviewer.value.id,
      deadline: deadline.value ? new Date(deadline.value).toISOString() : undefined,
      editor_comments: editorNote.value.trim() || undefined,
    })
    toast.success(t('review.assigned_success'))
    selectedReviewer.value = null
    editorNote.value = ''
    deadline.value = defaultDeadline
    await loadData()
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || t('common.error'))
  } finally {
    assigning.value = false
  }
}

async function sendDecision() {
  if (!decision.value) return
  deciding.value = true
  try {
    await api.post(`/api/articles/${articleId.value}/decision`, {
      decision: decision.value,
      comments_to_author: decisionComments.value.trim() || undefined,
    })
    toast.success(t('review.decision_sent'))
    await loadData()
    decision.value = ''
    decisionComments.value = ''
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || t('common.error'))
  } finally {
    deciding.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
    <!-- Back -->
    <RouterLink to="/admin/articles" class="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-white">
      <ChevronLeft class="h-4 w-4" />{{ t('common.back') }}
    </RouterLink>

    <!-- Skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-10 w-2/3 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
      <div class="h-48 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700" />
      <div class="h-64 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700" />
    </div>

    <template v-else-if="article">
      <!-- Article header -->
      <div class="mb-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="flex flex-wrap items-start justify-between gap-3">
          <div class="min-w-0">
            <h1 class="font-serif text-xl font-bold text-slate-900 dark:text-white">{{ articleTitle }}</h1>
            <div class="mt-2 flex flex-wrap gap-4 text-sm text-slate-500 dark:text-slate-400">
              <span v-if="article.author">{{ article.author.full_name }}</span>
              <span v-if="article.submission_date">{{ formatDateShort(article.submission_date) }}</span>
            </div>
          </div>
          <ArticleStatusBadge :status="article.status" />
        </div>
      </div>

      <!-- ── Assign Reviewer ─────────────────────────────────────────── -->
      <div class="mb-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
          <UserPlus class="h-5 w-5 text-indigo-500" />
          {{ t('review.assignReviewer') }}
          <span class="text-sm font-normal text-slate-400">({{ activeReviews.length }}/3)</span>
        </h2>

        <div class="grid gap-4 sm:grid-cols-2">
          <!-- Reviewer search -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('review.reviewer') }}</label>
            <ReviewerSearchDropdown v-model="selectedReviewer" />
          </div>

          <!-- Deadline -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('review.deadline') }}</label>
            <input
              v-model="deadline"
              type="date"
              :min="new Date().toISOString().split('T')[0]"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-400 focus:outline-none dark:border-slate-600 dark:bg-slate-900 dark:text-white"
              :class="shortDeadlineWarning ? 'border-amber-400' : ''"
            />
            <p v-if="shortDeadlineWarning" class="mt-1 text-xs text-amber-600 dark:text-amber-400">
              <AlertCircle class="mb-0.5 mr-1 inline h-3.5 w-3.5" />{{ t('review.short_deadline_warning') }}
            </p>
          </div>
        </div>

        <!-- Editor note -->
        <div class="mt-4">
          <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('review.assignNote') }}</label>
          <textarea
            v-model="editorNote"
            rows="2"
            class="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm placeholder-slate-400 focus:border-indigo-400 focus:outline-none dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            :placeholder="t('review.assignNotePlaceholder')"
          />
        </div>

        <div class="mt-4 flex items-center justify-between">
          <p v-if="activeReviews.length >= 3" class="text-sm text-amber-600 dark:text-amber-400">
            {{ t('review.max_reviewers_reached') }}
          </p>
          <button
            class="ml-auto flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-40"
            :disabled="!selectedReviewer || activeReviews.length >= 3 || assigning"
            @click="assignReviewer"
          >
            <UserPlus class="h-4 w-4" />
            {{ t('review.assign_btn') }}
          </button>
        </div>
      </div>

      <!-- ── Reviews panel ───────────────────────────────────────────── -->
      <div class="mb-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-5 text-base font-semibold text-slate-900 dark:text-white">
          {{ t('review.reviewers') }}
          <span class="ml-2 text-sm font-normal text-slate-400">{{ reviews.length }}</span>
        </h2>

        <div v-if="reviews.length === 0" class="py-8 text-center text-sm text-slate-400">
          {{ t('review.no_reviews') }}
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="r in reviews"
            :key="r.id"
            class="overflow-hidden rounded-xl border border-slate-200 dark:border-slate-700"
          >
            <!-- Row header -->
            <div class="flex flex-wrap items-center gap-3 bg-slate-50 px-4 py-3 dark:bg-slate-800/50">
              <!-- Avatar -->
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
                {{ r.reviewer ? initials(r.reviewer.full_name) : '?' }}
              </div>
              <!-- Name + affiliation -->
              <div class="min-w-0 flex-1">
                <p class="font-medium text-slate-900 dark:text-white">{{ r.reviewer?.full_name ?? '—' }}</p>
                <p v-if="r.reviewer?.affiliation" class="truncate text-xs text-slate-500">{{ r.reviewer.affiliation }}</p>
              </div>
              <!-- Status badge -->
              <span
                class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="{
                  'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300': r.status === 'pending',
                  'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300': r.status === 'accepted',
                  'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300': r.status === 'completed',
                  'bg-slate-100 text-slate-500 dark:bg-slate-700 dark:text-slate-400': r.status === 'declined',
                }"
              >
                <component :is="statusIcon(r.status)" class="h-3 w-3" :class="statusIconClass(r.status)" />
                {{ t(`review.status.${r.status}`) }}
              </span>
              <!-- Deadline -->
              <span v-if="r.deadline" class="text-xs" :class="deadlineClass(r.deadline)">
                {{ formatDateShort(r.deadline) }}
                <template v-if="daysLeft(r.deadline) !== null">
                  ({{ daysLeft(r.deadline)! < 0 ? t('review.overdue') : `${daysLeft(r.deadline)}d` }})
                </template>
              </span>
              <!-- Recommendation -->
              <RecommendationBadge v-if="r.recommendation" :recommendation="r.recommendation" />
              <!-- Expand toggle (for completed) -->
              <button
                v-if="r.status === 'completed'"
                class="ml-auto rounded p-1 text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700"
                @click="expandedReview = expandedReview === r.id ? null : r.id"
              >
                <component :is="expandedReview === r.id ? ChevronUp : ChevronDown" class="h-4 w-4" />
              </button>
            </div>

            <!-- Expanded: review content -->
            <div v-if="expandedReview === r.id" class="divide-y divide-slate-100 dark:divide-slate-700">
              <div v-if="r.comments_to_author" class="px-4 py-4">
                <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{{ t('review.commentsToAuthor') }}</p>
                <p class="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">{{ r.comments_to_author }}</p>
              </div>
              <div v-if="r.comments_to_editor" class="px-4 py-4">
                <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-400">{{ t('review.confidentialComments') }}</p>
                <p class="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300">{{ r.comments_to_editor }}</p>
              </div>
            </div>

            <!-- Declined reason -->
            <div v-if="r.status === 'declined' && r.decline_reason" class="bg-red-50 px-4 py-3 dark:bg-red-900/10">
              <p class="text-xs text-red-600 dark:text-red-400">{{ t('review.decline_reason') }}: {{ r.decline_reason }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Make Decision ───────────────────────────────────────────── -->
      <div class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-5 flex items-center gap-2 text-base font-semibold text-slate-900 dark:text-white">
          <Send class="h-5 w-5 text-indigo-500" />
          {{ t('review.makeDecision') }}
        </h2>

        <!-- Warning: no completed reviews -->
        <div v-if="!hasCompletedReviews" class="mb-4 flex items-start gap-2 rounded-lg bg-amber-50 p-3 text-sm text-amber-700 dark:bg-amber-900/20 dark:text-amber-400">
          <AlertCircle class="mt-0.5 h-4 w-4 shrink-0" />
          {{ t('decision.warning_no_reviews') }}
        </div>

        <!-- Decision radio cards -->
        <div class="mb-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div
            v-for="opt in decisionOptions"
            :key="opt.value"
            :class="decisionCardClass(opt.value)"
            @click="decision = opt.value"
          >
            {{ t(opt.label) }}
          </div>
        </div>

        <!-- Comments to author -->
        <div class="mb-5">
          <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
            {{ t('decision.comments_to_author') }}
          </label>
          <textarea
            v-model="decisionComments"
            rows="4"
            class="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm placeholder-slate-400 focus:border-indigo-400 focus:outline-none dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            :placeholder="t('decision.comments_placeholder')"
          />
        </div>

        <div class="flex justify-end">
          <button
            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-40"
            :disabled="!decision || deciding"
            @click="sendDecision"
          >
            <Send class="h-4 w-4" />
            {{ t('decision.send') }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>
