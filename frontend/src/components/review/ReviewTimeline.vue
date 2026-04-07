<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Send, Eye, CheckCircle, XCircle, AlertCircle, BookOpen } from 'lucide-vue-next'
import { formatDateShort } from '@/utils/formatDate'

interface ReviewEvent {
  id: string
  status: string
  recommendation: string | null
  created_at: string
  accepted_at: string | null
  declined_at: string | null
  submitted_at: string | null
  invitation_sent_at: string | null
}

const props = defineProps<{ review: ReviewEvent }>()
const { t } = useI18n()

interface Step {
  key: string
  icon: unknown
  color: string
  date: string | null
  active: boolean
  done: boolean
}

const steps = computed((): Step[] => {
  const r = props.review
  const statusOrder = ['pending', 'accepted', 'completed', 'declined']
  const currentIdx = statusOrder.indexOf(r.status)

  return [
    {
      key: 'invitation_sent',
      icon: Send,
      color: 'indigo',
      date: r.invitation_sent_at,
      done: !!r.invitation_sent_at,
      active: r.status === 'pending',
    },
    {
      key: r.status === 'declined' ? 'declined' : 'accepted',
      icon: r.status === 'declined' ? XCircle : CheckCircle,
      color: r.status === 'declined' ? 'red' : 'green',
      date: r.status === 'declined' ? r.declined_at : r.accepted_at,
      done: r.status !== 'pending',
      active: r.status === 'accepted',
    },
    {
      key: 'submitted',
      icon: BookOpen,
      color: 'blue',
      date: r.submitted_at,
      done: r.status === 'completed',
      active: r.status === 'completed',
    },
  ]
})
</script>

<template>
  <div class="space-y-0">
    <div
      v-for="(step, i) in steps"
      :key="step.key"
      class="flex gap-3"
    >
      <!-- Icon + connector -->
      <div class="flex flex-col items-center">
        <div
          class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 transition-colors"
          :class="{
            'border-indigo-500 bg-indigo-50 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400': step.done && step.color === 'indigo',
            'border-green-500 bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400': step.done && step.color === 'green',
            'border-blue-500 bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400': step.done && step.color === 'blue',
            'border-red-500 bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400': step.done && step.color === 'red',
            'border-slate-300 bg-white text-slate-300 dark:border-slate-600 dark:bg-slate-800': !step.done,
          }"
        >
          <component :is="step.icon" class="h-4 w-4" />
        </div>
        <div
          v-if="i < steps.length - 1"
          class="my-1 h-6 w-0.5"
          :class="step.done ? 'bg-slate-300 dark:bg-slate-600' : 'bg-slate-200 dark:bg-slate-700'"
        />
      </div>

      <!-- Content -->
      <div class="pb-4">
        <p
          class="text-sm font-medium"
          :class="step.done ? 'text-slate-900 dark:text-white' : 'text-slate-400 dark:text-slate-500'"
        >
          {{ $t(`review.timeline.${step.key}`, step.key) }}
        </p>
        <p v-if="step.date" class="text-xs text-slate-500 dark:text-slate-400">
          {{ formatDateShort(step.date) }}
        </p>
        <RecommendationBadge
          v-if="step.key === 'submitted' && review.recommendation"
          :recommendation="review.recommendation"
          class="mt-1"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import RecommendationBadge from './RecommendationBadge.vue'
export default { components: { RecommendationBadge } }
</script>
