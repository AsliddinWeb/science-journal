<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useApi } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import {
  ChevronLeft, Download, CheckCircle, Edit, AlertCircle, XCircle, CloudLightning, Send,
} from 'lucide-vue-next'

interface ReviewDetail {
  id: string
  article_id: string
  status: string
  recommendation: string | null
  deadline: string | null
  editor_comments: string | null
  created_at: string
  article: {
    id: string
    title: Record<string, string>
    abstract: Record<string, string>
    language: string
    category_id: string | null
    submission_date: string | null
    pdf_file_path: string | null
  } | null
}

const DRAFT_KEY_PREFIX = 'review_draft_'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()
const localeStore = useLocaleStore()

const reviewId = computed(() => route.params.reviewId as string)
const review = ref<ReviewDetail | null>(null)
const loading = ref(true)
const submitting = ref(false)
const showConfirmModal = ref(false)
const draftSavedAt = ref<Date | null>(null)
let autosaveTimer: ReturnType<typeof setInterval> | null = null

// Form state
const recommendation = ref<string>('')
const commentsToAuthor = ref('')
const commentsToEditor = ref('')
const checklist = ref({ readFull: false, noConflict: false, objective: false })

// Draft persistence
const DRAFT_KEY = computed(() => `${DRAFT_KEY_PREFIX}${reviewId.value}`)

function saveDraft() {
  if (!recommendation.value && !commentsToAuthor.value) return
  localStorage.setItem(DRAFT_KEY.value, JSON.stringify({
    recommendation: recommendation.value,
    commentsToAuthor: commentsToAuthor.value,
    commentsToEditor: commentsToEditor.value,
  }))
  draftSavedAt.value = new Date()
}

function restoreDraft() {
  const raw = localStorage.getItem(DRAFT_KEY.value)
  if (!raw) return
  try {
    const d = JSON.parse(raw)
    recommendation.value = d.recommendation ?? ''
    commentsToAuthor.value = d.commentsToAuthor ?? ''
    commentsToEditor.value = d.commentsToEditor ?? ''
    draftSavedAt.value = new Date()
  } catch {}
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY.value)
}

onMounted(async () => {
  loading.value = true
  try {
    review.value = await api.get<ReviewDetail>(`/api/reviews/${reviewId.value}`)
    restoreDraft()
    autosaveTimer = setInterval(saveDraft, 60_000)
  } catch {
    toast.error(t('common.error'))
  } finally {
    loading.value = false
  }
})

onUnmounted(() => {
  if (autosaveTimer) clearInterval(autosaveTimer)
})

const title = computed(() => {
  if (!review.value?.article) return ''
  return getLocalizedField(review.value.article.title, localeStore.current) || ''
})

const abstract = computed(() => {
  if (!review.value?.article) return ''
  return getLocalizedField(review.value.article.abstract, localeStore.current) || ''
})

const daysLeft = computed(() => {
  if (!review.value?.deadline) return null
  return Math.ceil((new Date(review.value.deadline).getTime() - Date.now()) / 86400000)
})

const deadlineColor = computed(() => {
  if (daysLeft.value === null) return 'text-slate-400'
  if (daysLeft.value < 0) return 'text-red-600 font-semibold dark:text-red-400'
  if (daysLeft.value <= 3) return 'text-red-500 dark:text-red-400'
  if (daysLeft.value <= 7) return 'text-amber-500 dark:text-amber-400'
  return 'text-green-600 dark:text-green-400'
})

const recommendations = [
  { value: 'accept', icon: CheckCircle, color: 'green', label: 'review.recommendation.accept' },
  { value: 'minor_revision', icon: Edit, color: 'blue', label: 'review.recommendation.minor_revision' },
  { value: 'major_revision', icon: AlertCircle, color: 'amber', label: 'review.recommendation.major_revision' },
  { value: 'reject', icon: XCircle, color: 'red', label: 'review.recommendation.reject' },
]

const recCardClass = (value: string) => {
  const selected = recommendation.value === value
  const base = 'cursor-pointer rounded-xl border-2 p-4 transition-all'
  if (!selected) return `${base} border-slate-200 hover:border-slate-300 dark:border-slate-700`
  const colors: Record<string, string> = {
    accept: 'border-green-500 bg-green-50 dark:border-green-600 dark:bg-green-900/20',
    minor_revision: 'border-blue-500 bg-blue-50 dark:border-blue-600 dark:bg-blue-900/20',
    major_revision: 'border-amber-500 bg-amber-50 dark:border-amber-600 dark:bg-amber-900/20',
    reject: 'border-red-500 bg-red-50 dark:border-red-600 dark:bg-red-900/20',
  }
  return `${base} ${colors[value] ?? ''}`
}

const iconColor = (value: string, selected: boolean) => {
  if (!selected) return 'text-slate-400'
  const colors: Record<string, string> = {
    accept: 'text-green-600 dark:text-green-400',
    minor_revision: 'text-blue-600 dark:text-blue-400',
    major_revision: 'text-amber-600 dark:text-amber-400',
    reject: 'text-red-600 dark:text-red-400',
  }
  return colors[value] ?? ''
}

const canSubmit = computed(() =>
  recommendation.value &&
  commentsToAuthor.value.trim().length >= 50 &&
  checklist.value.readFull &&
  checklist.value.noConflict &&
  checklist.value.objective
)

async function getPdfUrl() {
  try {
    const data = await api.get<{ download_url: string }>(`/api/articles/${review.value?.article_id}/download`)
    window.open(data.download_url, '_blank')
  } catch {
    toast.error(t('common.error'))
  }
}

function openConfirm() {
  if (!canSubmit.value) return
  showConfirmModal.value = true
}

async function submitReview() {
  if (!canSubmit.value) return
  submitting.value = true
  showConfirmModal.value = false
  try {
    await api.post(`/api/reviews/${reviewId.value}/submit`, {
      recommendation: recommendation.value,
      comments_to_author: commentsToAuthor.value.trim(),
      comments_to_editor: commentsToEditor.value.trim() || undefined,
    })
    clearDraft()
    toast.success(t('review.submit_success'))
    router.push('/reviewer/dashboard')
  } catch (err: any) {
    toast.error(err?.response?.data?.detail || t('common.error'))
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
    <!-- Back -->
    <RouterLink to="/reviewer/dashboard" class="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 dark:hover:text-white">
      <ChevronLeft class="h-4 w-4" />{{ t('common.back') }}
    </RouterLink>

    <!-- Loading skeleton -->
    <div v-if="loading" class="space-y-4">
      <div class="h-8 w-2/3 animate-pulse rounded-lg bg-slate-200 dark:bg-slate-700" />
      <div class="h-32 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700" />
      <div class="h-64 animate-pulse rounded-xl bg-slate-200 dark:bg-slate-700" />
    </div>

    <template v-else-if="review">
      <!-- Article header -->
      <div class="mb-6 rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h1 class="mb-2 font-serif text-xl font-bold text-slate-900 dark:text-white">{{ title }}</h1>
        <div class="mb-4 flex flex-wrap gap-4 text-sm text-slate-500 dark:text-slate-400">
          <span v-if="review.article?.submission_date">{{ t('review.submitted_date') }}: {{ formatDateShort(review.article.submission_date) }}</span>
          <span v-if="review.deadline" :class="deadlineColor">
            {{ t('review.deadline') }}: {{ formatDateShort(review.deadline) }}
            <template v-if="daysLeft !== null">
              ({{ daysLeft < 0 ? t('review.overdue') : `${daysLeft} ${t('review.daysLeft')}` }})
            </template>
          </span>
        </div>
        <p class="mb-4 text-sm leading-relaxed text-slate-600 dark:text-slate-300">{{ abstract }}</p>

        <!-- Download PDF -->
        <button
          class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700"
          @click="getPdfUrl"
        >
          <Download class="h-4 w-4" />
          {{ t('review.download_pdf') }}
        </button>
      </div>

      <!-- Editor note (if any) -->
      <div v-if="review.editor_comments" class="mb-6 rounded-xl border border-indigo-200 bg-indigo-50 p-4 dark:border-indigo-800 dark:bg-indigo-900/20">
        <p class="mb-1 text-xs font-semibold uppercase tracking-wide text-indigo-600 dark:text-indigo-400">{{ t('review.editor_note') }}</p>
        <p class="text-sm text-slate-700 dark:text-slate-300">{{ review.editor_comments }}</p>
      </div>

      <!-- Already completed notice -->
      <div v-if="review.status === 'completed'" class="mb-6 rounded-xl border border-green-200 bg-green-50 p-5 dark:border-green-800 dark:bg-green-900/20">
        <div class="flex items-center gap-2 text-green-700 dark:text-green-400">
          <CheckCircle class="h-5 w-5" />
          <p class="font-semibold">{{ t('review.already_submitted') }}</p>
        </div>
      </div>

      <!-- Review form (only if not completed) -->
      <div v-if="review.status !== 'completed'" class="space-y-6">
        <!-- Draft saved indicator -->
        <div v-if="draftSavedAt" class="flex items-center gap-1.5 text-xs text-slate-400 dark:text-slate-500">
          <CloudLightning class="h-3.5 w-3.5" />
          {{ t('review.draft_saved') }} {{ formatDateShort(draftSavedAt.toISOString()) }}
        </div>

        <!-- Recommendation cards -->
        <div>
          <label class="mb-3 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('review.recommendation_label') }} <span class="text-red-500">*</span>
          </label>
          <div class="grid grid-cols-2 gap-3">
            <div
              v-for="rec in recommendations"
              :key="rec.value"
              :class="recCardClass(rec.value)"
              @click="recommendation = rec.value"
            >
              <div class="flex items-center gap-2">
                <component :is="rec.icon" class="h-5 w-5" :class="iconColor(rec.value, recommendation === rec.value)" />
                <span class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ t(rec.label) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Comments to author -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('review.commentsToAuthor') }} <span class="text-red-500">*</span>
          </label>
          <p class="mb-2 text-xs text-slate-500 dark:text-slate-400">{{ t('review.commentsToAuthorHint') }}</p>
          <textarea
            v-model="commentsToAuthor"
            rows="7"
            class="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/20 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            :placeholder="t('review.commentsToAuthorPlaceholder')"
          />
          <p class="mt-1 text-right text-xs" :class="commentsToAuthor.trim().length < 50 ? 'text-red-400' : 'text-slate-400'">
            {{ commentsToAuthor.trim().length }} / 50 {{ t('review.chars_min') }}
          </p>
        </div>

        <!-- Confidential comments -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('review.confidentialComments') }}
          </label>
          <p class="mb-2 text-xs text-slate-500 dark:text-slate-400">{{ t('review.confidentialHint') }}</p>
          <textarea
            v-model="commentsToEditor"
            rows="4"
            class="w-full resize-none rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/20 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
            :placeholder="t('review.confidentialPlaceholder')"
          />
        </div>

        <!-- Checklist -->
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/50">
          <p class="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">{{ t('review.checklist_title') }}</p>
          <div class="space-y-2.5">
            <label class="flex cursor-pointer items-start gap-3">
              <input v-model="checklist.readFull" type="checkbox" class="mt-0.5 h-4 w-4 rounded accent-indigo-600" />
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('review.checklist.read_full') }}</span>
            </label>
            <label class="flex cursor-pointer items-start gap-3">
              <input v-model="checklist.noConflict" type="checkbox" class="mt-0.5 h-4 w-4 rounded accent-indigo-600" />
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('review.checklist.no_conflict') }}</span>
            </label>
            <label class="flex cursor-pointer items-start gap-3">
              <input v-model="checklist.objective" type="checkbox" class="mt-0.5 h-4 w-4 rounded accent-indigo-600" />
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('review.checklist.objective') }}</span>
            </label>
          </div>
        </div>

        <!-- Submit -->
        <div class="flex justify-end gap-3 pt-2">
          <RouterLink to="/reviewer/dashboard" class="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800">
            {{ t('common.cancel') }}
          </RouterLink>
          <button
            class="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 font-semibold text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-40"
            :disabled="!canSubmit || submitting"
            @click="openConfirm"
          >
            <Send class="h-4 w-4" />
            {{ t('review.submit_review') }}
          </button>
        </div>
      </div>
    </template>

    <!-- Confirm modal -->
    <Teleport to="body">
      <div v-if="showConfirmModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
        <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-2xl dark:bg-slate-800">
          <h2 class="mb-3 font-semibold text-slate-900 dark:text-white">{{ t('review.confirm_submit_title') }}</h2>
          <p class="mb-6 text-sm text-slate-600 dark:text-slate-400">{{ t('review.confirm_submit') }}</p>
          <div class="flex justify-end gap-3">
            <button class="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700" @click="showConfirmModal = false">
              {{ t('common.cancel') }}
            </button>
            <button class="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700" :disabled="submitting" @click="submitReview">
              <Send class="h-4 w-4" />
              {{ t('review.confirm_yes') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
