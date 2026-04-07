<script setup lang="ts">
import { Sun, Moon } from 'lucide-vue-next'
import { useDarkMode } from '@/composables/useDarkMode'

const props = withDefaults(defineProps<{
  variant?: 'navbar' | 'admin'
}>(), { variant: 'navbar' })

const { isDark, toggle } = useDarkMode()
</script>

<template>
  <button
    class="rounded-lg p-2 transition-colors"
    :class="variant === 'navbar'
      ? 'text-primary-300/80 hover:bg-white/10 hover:text-primary-200'
      : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200'"
    :title="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
    @click="toggle"
  >
    <Transition
      enter-active-class="transition-all duration-200"
      enter-from-class="opacity-0 rotate-90 scale-50"
      leave-active-class="transition-all duration-200"
      leave-to-class="opacity-0 -rotate-90 scale-50"
      mode="out-in"
    >
      <Sun v-if="isDark" :size="20" key="sun" />
      <Moon v-else :size="20" key="moon" />
    </Transition>
  </button>
</template>
