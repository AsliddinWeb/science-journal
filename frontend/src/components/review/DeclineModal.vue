<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { X, XCircle } from 'lucide-vue-next'

const props = defineProps<{ reviewId: string; loading?: boolean }>()
const emit = defineEmits<{
  confirm: [id: string, reason: string]
  cancel: []
}>()

const { t } = useI18n()
const selectedReason = ref('')
const explanation = ref('')

const reasons = [
  { value: 'conflict_of_interest', label: () => t('review.declineModal.reason_conflict') },
  { value: 'too_busy', label: () => t('review.declineModal.reason_busy') },
  { value: 'outside_expertise', label: () => t('review.declineModal.reason_expertise') },
  { value: 'other', label: () => t('review.declineModal.reason_other') },
]

function confirm() {
  const reason = explanation.value.trim()
    ? `${selectedReason.value}: ${explanation.value.trim()}`
    : selectedReason.value
  emit('confirm', props.reviewId, reason)
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div
        class="w-full max-w-md rounded-2xl bg-white shadow-2xl dark:bg-slate-800"
        role="dialog"
        aria-modal="true"
      >
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h2 class="font-semibold text-slate-900 dark:text-white">{{ t('review.declineModal.title') }}</h2>
          <button
            class="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 dark:hover:bg-slate-700"
            @click="emit('cancel')"
          >
            <X class="h-5 w-5" />
          </button>
        </div>

        <!-- Body -->
        <div class="space-y-4 px-6 py-5">
          <!-- Reason select -->
          <div class="space-y-2">
            <label
              v-for="r in reasons"
              :key="r.value"
              class="flex cursor-pointer items-center gap-3 rounded-lg border p-3 transition"
              :class="selectedReason === r.value
                ? 'border-red-400 bg-red-50 dark:border-red-600 dark:bg-red-900/20'
                : 'border-slate-200 hover:border-slate-300 dark:border-slate-700'"
            >
              <input
                v-model="selectedReason"
                type="radio"
                :value="r.value"
                class="accent-red-500"
              />
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ r.label() }}</span>
            </label>
          </div>

          <!-- Optional explanation -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('review.declineModal.explanation') }}
            </label>
            <textarea
              v-model="explanation"
              rows="3"
              class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 placeholder-slate-400 focus:border-red-400 focus:outline-none focus:ring-2 focus:ring-red-400/20 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
              :placeholder="t('review.declineModal.explanation')"
            />
          </div>
        </div>

        <!-- Footer -->
        <div class="flex justify-end gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-700">
          <button
            class="rounded-lg px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
            @click="emit('cancel')"
          >
            {{ t('common.cancel') }}
          </button>
          <button
            class="flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
            :disabled="!selectedReason || loading"
            @click="confirm"
          >
            <XCircle class="h-4 w-4" />
            {{ t('review.declineModal.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
