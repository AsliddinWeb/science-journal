<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { Home, BookOpen } from 'lucide-vue-next'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()
useSeoMeta({ title: t('errors.notFound') })
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-white px-4 dark:bg-slate-950">
    <!-- Illustration -->
    <svg
      class="mb-8 h-40 w-40 text-slate-200 dark:text-slate-800"
      viewBox="0 0 200 200"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <circle cx="100" cy="100" r="90" stroke="currentColor" stroke-width="6" />
      <path d="M65 80 Q80 60 100 80 Q120 100 135 80" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none" />
      <circle cx="75" cy="90" r="6" fill="currentColor" />
      <circle cx="125" cy="90" r="6" fill="currentColor" />
      <path d="M75 125 Q100 110 125 125" stroke="currentColor" stroke-width="5" stroke-linecap="round" fill="none" />
      <path d="M50 50 L60 40 M150 50 L140 40 M50 150 L60 160 M150 150 L140 160" stroke="currentColor" stroke-width="4" stroke-linecap="round" />
    </svg>

    <!-- 404 number -->
    <h1 class="mb-2 bg-gradient-to-r from-primary-600 to-primary-400 bg-clip-text font-serif text-8xl font-bold text-transparent dark:from-primary-400 dark:to-primary-300">
      404
    </h1>

    <h2 class="mb-3 font-serif text-2xl font-semibold text-slate-900 dark:text-white">
      {{ t('errors.notFound') }}
    </h2>

    <p class="mb-8 max-w-md text-center text-slate-500 dark:text-slate-400">
      {{ t('errors.notFoundMessage') }}
    </p>

    <div class="flex flex-wrap justify-center gap-3">
      <RouterLink
        to="/"
        class="btn-primary flex items-center gap-2"
      >
        <Home :size="16" />
        {{ t('errors.goHome') }}
      </RouterLink>
      <RouterLink
        to="/articles"
        class="btn-ghost flex items-center gap-2"
      >
        <BookOpen :size="16" />
        {{ t('nav.articles') }}
      </RouterLink>
    </div>
  </div>
</template>
