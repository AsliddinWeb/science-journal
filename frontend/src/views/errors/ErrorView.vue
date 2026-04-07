<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { RefreshCw, Home, ChevronDown, ChevronUp } from 'lucide-vue-next'
import { useSeoMeta } from '@/composables/useSeoMeta'

const props = withDefaults(defineProps<{
  error?: Error | string | null
  code?: number
}>(), {
  error: null,
  code: 500,
})

const { t } = useI18n()
useSeoMeta({ title: t('errors.serverError') })

const showDetails = ref(false)

const errorMessage = props.error instanceof Error
  ? props.error.message
  : (props.error ?? '')
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-white px-4 dark:bg-slate-950">
    <!-- Icon -->
    <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-red-50 dark:bg-red-950/30">
      <svg class="h-10 w-10 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      </svg>
    </div>

    <span class="mb-2 text-sm font-semibold uppercase tracking-widest text-red-500">{{ code }}</span>

    <h1 class="mb-3 font-serif text-3xl font-bold text-slate-900 dark:text-white">
      {{ t('errors.serverError') }}
    </h1>

    <p class="mb-8 max-w-md text-center text-slate-500 dark:text-slate-400">
      {{ t('errors.serverErrorMessage') }}
    </p>

    <div class="flex flex-wrap justify-center gap-3">
      <button
        class="btn-primary flex items-center gap-2"
        @click="() => window.location.reload()"
      >
        <RefreshCw :size="16" />
        {{ t('errors.tryAgain') }}
      </button>
      <RouterLink to="/" class="btn-ghost flex items-center gap-2">
        <Home :size="16" />
        {{ t('errors.goHome') }}
      </RouterLink>
    </div>

    <!-- Collapsible error details (dev only) -->
    <div v-if="errorMessage" class="mt-8 w-full max-w-lg">
      <button
        class="flex w-full items-center justify-between rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-500 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800"
        @click="showDetails = !showDetails"
      >
        <span>{{ t('errors.errorDetails') }}</span>
        <component :is="showDetails ? ChevronUp : ChevronDown" :size="15" />
      </button>
      <Transition
        enter-active-class="transition-all duration-200"
        leave-active-class="transition-all duration-200"
        enter-from-class="opacity-0 -translate-y-1"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <pre
          v-if="showDetails"
          class="mt-2 overflow-auto rounded-lg bg-slate-900 p-4 text-xs text-slate-300"
        >{{ errorMessage }}</pre>
      </Transition>
    </div>
  </div>
</template>
