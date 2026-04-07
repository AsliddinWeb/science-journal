<script setup lang="ts">
import { AlertTriangle } from 'lucide-vue-next'
import AppButton from '@/components/ui/AppButton.vue'

const props = defineProps<{
  title?: string
  message?: string
  confirmLabel?: string
  cancelLabel?: string
  loading?: boolean
  danger?: boolean
}>()

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="emit('cancel')" />
      <div class="relative w-full max-w-md rounded-2xl bg-white shadow-xl dark:bg-slate-800">
        <div class="p-6">
          <div class="flex gap-4">
            <div
              class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full"
              :class="danger ? 'bg-red-100 dark:bg-red-900/30' : 'bg-amber-100 dark:bg-amber-900/30'"
            >
              <AlertTriangle
                :size="20"
                :class="danger ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'"
              />
            </div>
            <div class="flex-1">
              <h3 class="font-semibold text-slate-900 dark:text-white">
                {{ title || 'Tasdiqlash' }}
              </h3>
              <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                {{ message || 'Bu amalni bajarishni istaysizmi?' }}
              </p>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-end gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-700">
          <AppButton variant="ghost" :disabled="loading" @click="emit('cancel')">
            {{ cancelLabel || 'Bekor qilish' }}
          </AppButton>
          <AppButton
            :variant="danger ? 'danger' : 'primary'"
            :loading="loading"
            @click="emit('confirm')"
          >
            {{ confirmLabel || 'Tasdiqlash' }}
          </AppButton>
        </div>
      </div>
    </div>
  </Teleport>
</template>
