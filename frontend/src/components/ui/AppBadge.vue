<script setup lang="ts">
import { computed } from 'vue'

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info'

interface Props {
  variant?: BadgeVariant
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  dot: false,
})

const classes = computed(() => {
  const base = 'inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium'
  const variants: Record<BadgeVariant, string> = {
    default: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    primary: 'bg-primary-100 text-primary-700 dark:bg-primary-950 dark:text-primary-300',
    success: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400',
    warning: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
    danger: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
    info: 'bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-400',
  }
  return [base, variants[props.variant]]
})

const dotColors: Record<BadgeVariant, string> = {
  default: 'bg-slate-400',
  primary: 'bg-primary-500',
  success: 'bg-green-500',
  warning: 'bg-amber-500',
  danger: 'bg-red-500',
  info: 'bg-sky-500',
}
</script>

<template>
  <span :class="classes">
    <span v-if="dot" class="h-1.5 w-1.5 rounded-full" :class="dotColors[variant]" />
    <slot />
  </span>
</template>
