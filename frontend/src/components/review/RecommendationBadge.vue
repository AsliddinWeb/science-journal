<script setup lang="ts">
defineProps<{ recommendation: string | null | undefined }>()
</script>

<template>
  <span
    v-if="recommendation"
    class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold"
    :class="{
      'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300': recommendation === 'accept',
      'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300': recommendation === 'minor_revision',
      'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300': recommendation === 'major_revision',
      'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300': recommendation === 'reject',
    }"
  >
    {{ $t(`review.recommendation.${recommendation}`) }}
  </span>
  <span v-else class="text-slate-400 text-xs">—</span>
</template>
