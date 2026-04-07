<script setup lang="ts">
withDefaults(defineProps<{
  lines?: number
  lastLineFraction?: number
}>(), {
  lines: 3,
  lastLineFraction: 0.6,
})
</script>

<template>
  <div class="animate-pulse space-y-2">
    <div
      v-for="i in lines"
      :key="i"
      class="h-3 rounded bg-slate-200 dark:bg-slate-700"
      :style="{ width: i === lines ? `${lastLineFraction * 100}%` : '100%' }"
    />
  </div>
</template>
