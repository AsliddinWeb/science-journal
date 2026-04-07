<script setup lang="ts">
import { X } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

interface Props {
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

defineEmits<{ close: [] }>()

const { t } = useI18n()

const sizeClasses: Record<string, string> = {
  sm: 'max-w-sm',
  md: 'max-w-lg',
  lg: 'max-w-2xl',
  xl: 'max-w-4xl',
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <div
        class="absolute inset-0 bg-black/50 backdrop-blur-sm"
        @click="$emit('close')"
      />

      <!-- Dialog -->
      <div
        class="relative w-full rounded-2xl border border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-800"
        :class="sizeClasses[size]"
      >
        <!-- Header -->
        <div v-if="title" class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h3 class="text-lg font-semibold text-slate-900 dark:text-white">{{ title }}</h3>
          <button
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
            @click="$emit('close')"
          >
            <X :size="18" />
          </button>
        </div>
        <button
          v-else
          class="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700"
          @click="$emit('close')"
        >
          <X :size="18" />
        </button>

        <!-- Content -->
        <div class="p-6">
          <slot />
        </div>

        <!-- Footer -->
        <div
          v-if="$slots.footer"
          class="flex items-center justify-end gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-700"
        >
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
