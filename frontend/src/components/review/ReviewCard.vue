<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import { CheckCircle, XCircle, Clock } from 'lucide-vue-next'

interface ReviewInvitation {
  id: string
  article_id: string
  status: string
  deadline: string | null
  created_at: string
  article: {
    id: string
    title: Record<string, string>
    language: string
  } | null
}

const props = defineProps<{ review: ReviewInvitation; loading?: boolean }>()
const emit = defineEmits<{
  accept: [id: string]
  decline: [id: string]
}>()

const { t } = useI18n()
const localeStore = useLocaleStore()

const title = computed(() =>
  props.review.article
    ? getLocalizedField(props.review.article.title, localeStore.current) || t('common.untitled')
    : `Article #${props.review.article_id.slice(0, 8)}`
)

const daysLeft = computed(() => {
  if (!props.review.deadline) return null
  const diff = new Date(props.review.deadline).getTime() - Date.now()
  return Math.ceil(diff / (1000 * 60 * 60 * 24))
})

const deadlineColor = computed(() => {
  if (daysLeft.value === null) return ''
  if (daysLeft.value < 0) return 'text-red-600 dark:text-red-400'
  if (daysLeft.value <= 3) return 'text-red-500 dark:text-red-400'
  if (daysLeft.value <= 7) return 'text-amber-500 dark:text-amber-400'
  return 'text-green-600 dark:text-green-400'
})
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800">
    <!-- Title -->
    <h3 class="mb-2 line-clamp-2 font-medium text-slate-900 dark:text-white">{{ title }}</h3>

    <!-- Deadline row -->
    <div class="mb-4 flex items-center gap-2 text-sm">
      <Clock class="h-4 w-4 shrink-0 text-slate-400" />
      <span v-if="review.deadline">
        {{ t('review.deadline') }}: {{ formatDateShort(review.deadline) }}
        <span v-if="daysLeft !== null" class="ml-1 font-semibold" :class="deadlineColor">
          <template v-if="daysLeft < 0">({{ t('review.overdue') }})</template>
          <template v-else>({{ daysLeft }} {{ t('review.daysLeft') }})</template>
        </span>
      </span>
      <span v-else class="text-slate-400">{{ t('review.deadline') }}: —</span>
    </div>

    <!-- Received date -->
    <p class="mb-4 text-xs text-slate-500 dark:text-slate-400">
      {{ t('review.assigned_date') }}: {{ formatDateShort(review.created_at) }}
    </p>

    <!-- Actions -->
    <div class="flex gap-2">
      <button
        class="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-green-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-green-700 disabled:opacity-50"
        :disabled="loading"
        @click="emit('accept', review.id)"
      >
        <CheckCircle class="h-4 w-4" />
        {{ t('review.accept') }}
      </button>
      <button
        class="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-red-300 px-3 py-2 text-sm font-semibold text-red-600 transition hover:bg-red-50 dark:border-red-700 dark:text-red-400 dark:hover:bg-red-900/20 disabled:opacity-50"
        :disabled="loading"
        @click="emit('decline', review.id)"
      >
        <XCircle class="h-4 w-4" />
        {{ t('review.decline') }}
      </button>
    </div>
  </div>
</template>
