<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  Home, BookText, Info, ChevronDown, Users, UserCheck,
  Archive as ArchiveIcon, Mail, Newspaper, Presentation,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import type { Volume } from '@/types/volume'

const { t } = useI18n()

const volumes = ref<Volume[]>([])
const openGroups = ref<Set<string>>(new Set(['info']))

function toggle(key: string) {
  if (openGroups.value.has(key)) openGroups.value.delete(key)
  else openGroups.value.add(key)
}

onMounted(async () => {
  try {
    volumes.value = await api.get<Volume[]>('/api/volumes')
  } catch { /* ignore */ }
})

const volumesByYear = computed(() => {
  const m = new Map<number, Volume[]>()
  volumes.value.forEach(v => {
    if (!m.has(v.year)) m.set(v.year, [])
    m.get(v.year)!.push(v)
  })
  return Array.from(m.entries()).sort((a, b) => b[0] - a[0])
})
</script>

<template>
  <aside class="w-full space-y-2">
    <!-- 1. Home -->
    <RouterLink
      to="/"
      exact-active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <Home :size="16" />
      {{ t('nav.home') }}
    </RouterLink>

    <!-- 2. Articles -->
    <RouterLink
      to="/articles"
      active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <Newspaper :size="16" />
      {{ t('nav.articles') }}
    </RouterLink>

    <!-- 3. Archive -->
    <RouterLink
      to="/archive"
      active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <ArchiveIcon :size="16" />
      {{ t('nav.archive') }}
    </RouterLink>

    <!-- 4. Conferences -->
    <RouterLink
      to="/conferences"
      active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <Presentation :size="16" />
      {{ t('nav.conferences') }}
    </RouterLink>

    <!-- 5. Editorial Board -->
    <RouterLink
      to="/editorial-board"
      active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <UserCheck :size="16" />
      {{ t('nav.editorial') }}
    </RouterLink>

    <!-- 6. Journal Info (collapsible) -->
    <div>
      <button
        class="flex w-full items-center justify-between gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
        @click="toggle('info')"
      >
        <span class="flex items-center gap-3">
          <Info :size="16" />
          {{ t('nav.about_journal') }}
        </span>
        <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': openGroups.has('info') }" />
      </button>
      <div v-if="openGroups.has('info')" class="mt-1 rounded-lg border border-stone-200 bg-white px-4 py-3 text-sm dark:border-slate-700 dark:bg-slate-800">
        <RouterLink to="/pages/about" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.about_journal') }}</RouterLink>
        <RouterLink to="/pages/aims" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.aims_scope') }}</RouterLink>
        <RouterLink to="/pages/indexing" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.indexing') }}</RouterLink>
        <RouterLink to="/pages/open-access" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.open_access') }}</RouterLink>
        <RouterLink to="/pages/privacy" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">Privacy</RouterLink>
      </div>
    </div>

    <!-- 7. For Authors (collapsible) -->
    <div>
      <button
        class="flex w-full items-center justify-between gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
        @click="toggle('authors')"
      >
        <span class="flex items-center gap-3">
          <BookText :size="16" />
          {{ t('nav.for_authors') }}
        </span>
        <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': openGroups.has('authors') }" />
      </button>
      <div v-if="openGroups.has('authors')" class="mt-1 rounded-lg border border-stone-200 bg-white px-4 py-3 text-sm dark:border-slate-700 dark:bg-slate-800">
        <RouterLink to="/pages/author-guidelines" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.author_guidelines') }}</RouterLink>
        <RouterLink to="/pages/review-process" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">{{ t('nav.review_process') }}</RouterLink>
        <RouterLink to="/pages/plagiarism" class="block py-1 text-slate-700 hover:text-primary-600 dark:text-slate-300">Plagiarism</RouterLink>
      </div>
    </div>

    <!-- 9. Contact -->
    <RouterLink
      to="/contact"
      active-class="!bg-primary-700 !text-white"
      class="flex items-center gap-3 rounded-lg bg-journal-900 px-4 py-3 text-sm font-medium text-slate-200 transition hover:bg-journal-800"
    >
      <Mail :size="16" />
      {{ t('nav.contact') }}
    </RouterLink>

    <!-- Volumes (collapsible) -->
    <div v-for="[year, vols] in volumesByYear" :key="year" class="mt-1">
      <button
        class="flex w-full items-center justify-between gap-3 rounded-lg bg-white border border-stone-200 px-4 py-3 text-sm font-semibold text-journal-800 transition hover:bg-stone-50 hover:border-primary-300 dark:bg-slate-800 dark:border-slate-700 dark:text-primary-300 dark:hover:bg-slate-700"
        @click="toggle(`vol-${year}`)"
      >
        <span>Volume {{ year - 2023 }} ({{ year }})</span>
        <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': openGroups.has(`vol-${year}`) }" />
      </button>
      <div v-if="openGroups.has(`vol-${year}`)" class="mt-1 space-y-0.5 rounded-lg border border-stone-200 bg-white px-4 py-2 dark:border-slate-700 dark:bg-slate-800">
        <template v-for="v in vols" :key="v.id">
          <RouterLink
            v-for="iss in v.issues"
            :key="iss.id"
            :to="`/archive/${v.id}/issues/${iss.id}`"
            class="block py-1 text-xs text-slate-600 hover:text-primary-600 dark:text-slate-400"
          >
            📄 Issue {{ iss.number }}
          </RouterLink>
        </template>
      </div>
    </div>
  </aside>
</template>
