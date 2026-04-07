<script setup lang="ts">
import { computed } from 'vue'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'

interface Props {
  // New API (public views): currentPage + totalPages + @change
  currentPage?: number
  totalPages?: number
  // Legacy API (admin views): page + pages + total + limit + @update:page
  page?: number
  pages?: number
  total?: number
  limit?: number
}

const props = withDefaults(defineProps<Props>(), {
  currentPage: undefined,
  totalPages: undefined,
  page: undefined,
  pages: undefined,
  total: 0,
  limit: 10,
})

const emit = defineEmits<{
  change: [page: number]
  'update:page': [page: number]
}>()

// Resolve which API is being used
const activePage = computed(() => props.currentPage ?? props.page ?? 1)
const activePages = computed(() => props.totalPages ?? props.pages ?? 1)

const pageNumbers = computed(() => {
  const delta = 2
  const range: (number | '...')[] = []
  const total = activePages.value

  for (let i = Math.max(2, activePage.value - delta); i <= Math.min(total - 1, activePage.value + delta); i++) {
    range.push(i)
  }

  if (activePage.value - delta > 2) range.unshift('...')
  if (activePage.value + delta < total - 1) range.push('...')

  range.unshift(1)
  if (total > 1) range.push(total)

  return range
})

function goTo(p: number) {
  if (p < 1 || p > activePages.value || p === activePage.value) return
  emit('change', p)
  emit('update:page', p)
}
</script>

<template>
  <div v-if="activePages > 1" class="flex items-center justify-between gap-4">
    <p v-if="total && limit" class="text-sm text-slate-500 dark:text-slate-400">
      Showing {{ (activePage - 1) * limit + 1 }}–{{ Math.min(activePage * limit, total) }} of {{ total }}
    </p>
    <div v-else />

    <div class="flex items-center gap-1">
      <button
        :disabled="activePage === 1"
        class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed dark:text-slate-400 dark:hover:bg-slate-800"
        @click="goTo(activePage - 1)"
      >
        <ChevronLeft :size="16" />
      </button>

      <template v-for="(p, i) in pageNumbers" :key="i">
        <button
          v-if="p !== '...'"
          class="min-w-[36px] rounded-lg px-2 py-1.5 text-sm font-medium transition-colors"
          :class="
            p === activePage
              ? 'bg-primary-600 text-white'
              : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
          "
          @click="goTo(p as number)"
        >
          {{ p }}
        </button>
        <span v-else class="px-1 text-slate-400">…</span>
      </template>

      <button
        :disabled="activePage === activePages"
        class="rounded-lg p-2 text-slate-500 hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed dark:text-slate-400 dark:hover:bg-slate-800"
        @click="goTo(activePage + 1)"
      >
        <ChevronRight :size="16" />
      </button>
    </div>
  </div>
</template>
