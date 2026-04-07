<script setup lang="ts">
import { ref } from 'vue'
import { Download } from 'lucide-vue-next'

const props = defineProps<{
  label?: string
  url: string
  filename?: string
}>()

const loading = ref(false)

async function doExport() {
  if (loading.value) return
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(props.url, {
      headers: { Authorization: `Bearer ${token}` },
    })
    if (!response.ok) throw new Error('Export failed')
    const blob = await response.blob()
    const href = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = href
    a.download = props.filename || 'export.csv'
    a.click()
    URL.revokeObjectURL(href)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <button
    class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
    :disabled="loading"
    @click="doExport"
  >
    <Download :size="15" :class="loading ? 'animate-bounce' : ''" />
    {{ loading ? 'Yuklanmoqda...' : (label || 'CSV yuklab olish') }}
  </button>
</template>
