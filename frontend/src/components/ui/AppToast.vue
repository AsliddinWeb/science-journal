<script setup lang="ts">
import { CheckCircle, XCircle, AlertTriangle, Info, X } from 'lucide-vue-next'
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()

const iconMap = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
}

const colorMap = {
  success: 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-950',
  error: 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950',
  warning: 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950',
  info: 'border-sky-200 bg-sky-50 dark:border-sky-800 dark:bg-sky-950',
}

const textColorMap = {
  success: 'text-green-800 dark:text-green-300',
  error: 'text-red-800 dark:text-red-300',
  warning: 'text-amber-800 dark:text-amber-300',
  info: 'text-sky-800 dark:text-sky-300',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 sm:bottom-6 sm:right-6">
      <TransitionGroup
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 translate-x-8 scale-95"
        leave-active-class="transition-all duration-200 ease-in"
        leave-to-class="opacity-0 translate-x-8 scale-95"
      >
        <div
          v-for="toast in toasts"
          :key="toast.id"
          class="flex w-80 items-start gap-3 rounded-xl border p-4 shadow-lg"
          :class="colorMap[toast.type]"
        >
          <component
            :is="iconMap[toast.type]"
            :size="20"
            :class="textColorMap[toast.type]"
            class="mt-0.5 shrink-0"
          />
          <p class="flex-1 text-sm font-medium" :class="textColorMap[toast.type]">
            {{ toast.message }}
          </p>
          <button
            class="shrink-0 rounded p-0.5 opacity-60 hover:opacity-100"
            :class="textColorMap[toast.type]"
            @click="dismiss(toast.id)"
          >
            <X :size="14" />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>
