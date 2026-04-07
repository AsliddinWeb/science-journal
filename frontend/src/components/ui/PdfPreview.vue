<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { X, Download } from 'lucide-vue-next'
import VueOfficePdf from '@vue-office/pdf'

const props = defineProps<{
  url: string
  title?: string
}>()

const emit = defineEmits<{ close: [] }>()

const pdfUrl = computed(() => {
  return props.url.startsWith('/') ? props.url : `/api/uploads/${props.url}`
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  document.body.style.overflow = 'hidden'
})
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-[100] flex flex-col bg-slate-900">
      <!-- Toolbar -->
      <div class="flex shrink-0 items-center justify-between bg-slate-800 px-4 py-2.5 shadow-lg">
        <h3 class="min-w-0 flex-1 truncate text-sm font-medium text-slate-200 mr-4">{{ title || 'PDF' }}</h3>
        <div class="flex items-center gap-1">
          <a
            :href="pdfUrl"
            download
            class="rounded-lg px-3 py-1.5 text-sm text-slate-300 transition hover:bg-slate-700 hover:text-white flex items-center gap-1.5"
          >
            <Download :size="16" />
            <span class="hidden sm:inline">Yuklab olish</span>
          </a>
          <button
            class="rounded-lg p-2 text-slate-400 transition hover:bg-red-600 hover:text-white"
            @click="emit('close')"
            title="Yopish (Esc)"
          >
            <X :size="18" />
          </button>
        </div>
      </div>

      <!-- PDF - all pages, scrollable -->
      <div class="flex-1 overflow-auto bg-slate-700">
        <VueOfficePdf :src="pdfUrl" class="pdf-viewer" />
      </div>
    </div>
  </Teleport>
</template>

<style>
.pdf-viewer {
  padding: 16px 0;
}
.pdf-viewer canvas {
  display: block;
  margin: 0 auto 16px auto;
  box-shadow: 0 4px 24px rgba(0,0,0,0.3);
  max-width: 100%;
}
</style>
