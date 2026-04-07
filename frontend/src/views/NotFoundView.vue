<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Home } from 'lucide-vue-next'

const { t } = useI18n()
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-white px-4 dark:bg-slate-950">
    <div class="text-center">
      <p class="text-8xl font-bold text-primary-600/20">404</p>
      <h1 class="mt-4 text-2xl font-bold text-slate-900 dark:text-white">
        {{ t('errors.404_title') }}
      </h1>
      <p class="mt-2 text-slate-500 dark:text-slate-400">{{ t('errors.404_desc') }}</p>
      <RouterLink
        to="/"
        class="btn-primary mt-8 inline-flex"
      >
        <Home :size="18" />
        {{ t('errors.go_home') }}
      </RouterLink>
    </div>
  </div>
</template>
