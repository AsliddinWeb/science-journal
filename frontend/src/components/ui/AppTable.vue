<script setup lang="ts" generic="T extends Record<string, unknown>">
import { ref, computed } from 'vue'
import { ChevronUp, ChevronDown } from 'lucide-vue-next'
import AppSpinner from './AppSpinner.vue'

export interface TableColumn<T> {
  key: string
  label: string
  sortable?: boolean
  class?: string
  headerClass?: string
}

interface Props {
  columns: TableColumn<T>[]
  rows: T[]
  loading?: boolean
  striped?: boolean
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  striped: true,
  emptyText: 'No data available',
})

const sortKey = ref<string | null>(null)
const sortDir = ref<'asc' | 'desc'>('asc')

function toggleSort(col: TableColumn<T>) {
  if (!col.sortable) return
  if (sortKey.value === col.key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = col.key
    sortDir.value = 'asc'
  }
}

const sortedRows = computed(() => {
  if (!sortKey.value) return props.rows
  return [...props.rows].sort((a, b) => {
    const aVal = a[sortKey.value!]
    const bVal = b[sortKey.value!]
    if (aVal === bVal) return 0
    const cmp = String(aVal) < String(bVal) ? -1 : 1
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})
</script>

<template>
  <div class="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
    <table class="w-full min-w-[600px] text-sm">
      <thead>
        <tr class="border-b border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800/50">
          <th
            v-for="col in columns"
            :key="col.key"
            class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400"
            :class="[col.headerClass, col.sortable ? 'cursor-pointer select-none hover:text-slate-700 dark:hover:text-slate-200' : '']"
            @click="toggleSort(col)"
          >
            <span class="flex items-center gap-1">
              {{ col.label }}
              <span v-if="col.sortable" class="opacity-60">
                <ChevronUp v-if="sortKey === col.key && sortDir === 'asc'" :size="12" />
                <ChevronDown v-else-if="sortKey === col.key && sortDir === 'desc'" :size="12" />
                <ChevronDown v-else :size="12" class="opacity-0 group-hover:opacity-100" />
              </span>
            </span>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td :colspan="columns.length" class="py-12 text-center">
            <AppSpinner :size="32" class="mx-auto text-primary-500" />
          </td>
        </tr>
        <tr v-else-if="sortedRows.length === 0">
          <td :colspan="columns.length" class="py-12 text-center text-sm text-slate-500 dark:text-slate-400">
            {{ emptyText }}
          </td>
        </tr>
        <template v-else>
          <tr
            v-for="(row, idx) in sortedRows"
            :key="idx"
            class="border-b border-slate-100 transition-colors last:border-0 dark:border-slate-700/50"
            :class="striped && idx % 2 === 1 ? 'bg-slate-50/50 dark:bg-slate-800/30' : ''"
          >
            <td
              v-for="col in columns"
              :key="col.key"
              class="px-4 py-3 text-slate-700 dark:text-slate-300"
              :class="col.class"
            >
              <slot :name="col.key" :row="row" :value="row[col.key]">
                {{ row[col.key] ?? '—' }}
              </slot>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>
