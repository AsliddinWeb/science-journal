<script setup lang="ts">
withDefaults(defineProps<{
  rows?: number
  columns?: number
  columnWidths?: string[]
}>(), {
  rows: 5,
  columns: 4,
  columnWidths: () => [],
})
</script>

<template>
  <div class="animate-pulse">
    <table class="w-full text-sm">
      <thead class="border-b border-slate-200 dark:border-slate-700">
        <tr>
          <th
            v-for="i in columns"
            :key="i"
            class="px-4 py-3"
          >
            <div
              class="h-3 rounded bg-slate-200 dark:bg-slate-700"
              :style="{ width: columnWidths[i - 1] || '70%' }"
            />
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="r in rows"
          :key="r"
          class="border-b border-slate-100 dark:border-slate-800"
        >
          <td
            v-for="c in columns"
            :key="c"
            class="px-4 py-3"
          >
            <div
              class="h-3 rounded bg-slate-100 dark:bg-slate-800"
              :style="{ width: columnWidths[c - 1] || (c === 1 ? '90%' : c === columns ? '50%' : '70%') }"
            />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
