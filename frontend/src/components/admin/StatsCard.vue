<script setup lang="ts">
import { TrendingUp, TrendingDown, Minus } from 'lucide-vue-next'

const props = defineProps<{
  label: string
  value: number | string
  icon: object | Function
  iconColor?: string
  iconBg?: string
  change?: number
  changeLabel?: string
  attention?: boolean
}>()
</script>

<template>
  <div
    class="rounded-xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
    :class="attention ? 'border-amber-200 dark:border-amber-800/50' : 'border-slate-200'"
  >
    <div class="flex items-start justify-between gap-3">
      <div
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl"
        :class="iconBg || 'bg-primary-50 dark:bg-primary-950'"
      >
        <component
          :is="icon"
          :size="20"
          :class="iconColor || 'text-primary-600 dark:text-primary-400'"
        />
      </div>
      <div v-if="change !== undefined" class="flex items-center gap-1 text-xs font-medium">
        <template v-if="change > 0">
          <TrendingUp :size="13" class="text-emerald-500" />
          <span class="text-emerald-600 dark:text-emerald-400">+{{ change }}%</span>
        </template>
        <template v-else-if="change < 0">
          <TrendingDown :size="13" class="text-red-500" />
          <span class="text-red-600 dark:text-red-400">{{ change }}%</span>
        </template>
        <template v-else>
          <Minus :size="13" class="text-slate-400" />
          <span class="text-slate-500">0%</span>
        </template>
      </div>
    </div>
    <div class="mt-3">
      <p class="text-2xl font-bold text-slate-900 dark:text-white">
        {{ typeof value === 'number' ? value.toLocaleString() : value }}
      </p>
      <p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{{ label }}</p>
      <p v-if="changeLabel" class="mt-1 text-xs text-slate-400">{{ changeLabel }}</p>
    </div>
  </div>
</template>
