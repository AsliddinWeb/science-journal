<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-vue-next'

type ArticleStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'revision_required'
  | 'accepted'
  | 'rejected'
  | 'published'

interface Props {
  status: ArticleStatus
  submissionDate?: string | null
  publishedDate?: string | null
}

const props = defineProps<Props>()
const { t, locale } = useI18n()

interface Step {
  key: string
  label: string
  date?: string | null
  state: 'done' | 'active' | 'pending' | 'skipped'
}

const statusOrder: ArticleStatus[] = [
  'submitted',
  'under_review',
  'accepted',
  'published',
]

const steps = computed<Step[]>(() => {
  const current = props.status

  // Special handling for rejected / revision_required
  const steps: Step[] = [
    {
      key: 'submitted',
      label: t('author.timeline.submitted'),
      date: props.submissionDate,
      state: 'pending',
    },
    {
      key: 'under_review',
      label: t('author.timeline.under_review'),
      date: null,
      state: 'pending',
    },
    {
      key: 'decision',
      label: t('author.timeline.decision'),
      date: null,
      state: 'pending',
    },
    {
      key: 'published',
      label: t('author.timeline.published'),
      date: props.publishedDate,
      state: 'pending',
    },
  ]

  // Mark states based on current status
  if (current === 'draft') {
    // Nothing done
    return steps
  }

  steps[0].state = 'done' // submitted ✓

  if (current === 'submitted') {
    steps[1].state = 'active'
    return steps
  }

  steps[1].state = 'done' // under_review ✓

  if (current === 'under_review') {
    steps[2].state = 'active'
    return steps
  }

  if (current === 'revision_required') {
    steps[2].state = 'active'
    steps[2].label = t('author.status.revision_required')
    return steps
  }

  if (current === 'rejected') {
    steps[2].state = 'skipped'
    steps[2].label = t('author.status.rejected')
    steps[3].state = 'skipped'
    return steps
  }

  if (current === 'accepted') {
    steps[2].state = 'done'
    steps[3].state = 'active'
    return steps
  }

  if (current === 'published') {
    steps[2].state = 'done'
    steps[3].state = 'done'
    return steps
  }

  return steps
})

function formatDate(d?: string | null): string {
  if (!d) return ''
  return new Intl.DateTimeFormat(locale.value, { year: 'numeric', month: 'short', day: 'numeric' }).format(new Date(d))
}
</script>

<template>
  <div class="relative">
    <!-- Vertical line -->
    <div class="absolute left-4 top-4 bottom-4 w-px bg-slate-200 dark:bg-slate-700" />

    <div class="space-y-6">
      <div
        v-for="(step, i) in steps"
        :key="step.key"
        class="relative flex items-start gap-4"
      >
        <!-- Circle -->
        <div
          class="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2"
          :class="{
            'border-primary-600 bg-primary-600': step.state === 'done',
            'border-primary-600 bg-white dark:bg-slate-950': step.state === 'active',
            'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-950': step.state === 'pending',
            'border-red-400 bg-white dark:bg-slate-950': step.state === 'skipped',
          }"
        >
          <CheckCircle v-if="step.state === 'done'" :size="18" class="text-white" />
          <Clock v-else-if="step.state === 'active'" :size="15" class="text-primary-600 dark:text-primary-400" />
          <XCircle v-else-if="step.state === 'skipped'" :size="15" class="text-red-500" />
          <span v-else class="text-xs font-medium text-slate-400">{{ i + 1 }}</span>
        </div>

        <!-- Content -->
        <div class="pb-2 pt-0.5">
          <p
            class="text-sm font-semibold"
            :class="{
              'text-slate-900 dark:text-white': step.state === 'done' || step.state === 'active',
              'text-slate-400 dark:text-slate-600': step.state === 'pending',
              'text-red-600 dark:text-red-400': step.state === 'skipped',
            }"
          >
            {{ step.label }}
          </p>
          <p v-if="step.date && step.state === 'done'" class="mt-0.5 text-xs text-slate-400 dark:text-slate-500">
            {{ formatDate(step.date) }}
          </p>
          <p v-else-if="step.state === 'pending'" class="mt-0.5 text-xs text-slate-400">
            {{ t('author.timeline.pending') }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
