<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Calendar, MapPin, Users, FileText, ChevronRight, Search, SlidersHorizontal, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { useSeoMeta } from '@/composables/useSeoMeta'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import type { Conference } from '@/types/conference'

const { t } = useI18n()
const localeStore = useLocaleStore()
const { apply: applySeo } = useSeoMeta()

const conferences = ref<Conference[]>([])
const loading = ref(true)
const searchQuery = ref('')
const yearFilter = ref('')

const years = computed(() => {
  const s = new Set(conferences.value.map(c => c.year))
  return Array.from(s).sort((a, b) => b - a)
})

const filtered = computed(() => {
  let list = conferences.value
  if (yearFilter.value) list = list.filter(c => c.year === parseInt(yearFilter.value))
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(c => {
      const t = getLocalizedField(c.title, localeStore.current, '').toLowerCase()
      const loc = (c.location || '').toLowerCase()
      return t.includes(q) || loc.includes(q)
    })
  }
  return list
})

onMounted(async () => {
  applySeo({ title: t('conferences.title') })
  try {
    const data = await api.get<{ items: Conference[] }>('/api/conferences')
    conferences.value = data.items
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <!-- Hero -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('conferences.title') }}</h1>
      <p class="mt-2 text-sm text-slate-300">{{ t('conferences.subtitle') }}</p>
    </section>

    <!-- Filter bar -->
    <div class="overflow-hidden rounded-xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="flex items-center gap-2 border-b border-stone-200 bg-stone-50 px-4 py-2.5 dark:border-slate-700 dark:bg-slate-900/50">
        <SlidersHorizontal :size="14" class="text-primary-600 dark:text-primary-400" />
        <span class="text-xs font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">{{ t('common.filter') }}</span>
      </div>
      <div class="flex flex-wrap items-end gap-3 p-4">
        <!-- Search -->
        <div class="min-w-0 flex-1">
          <label class="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-slate-500">{{ t('common.search') }}</label>
          <div class="relative">
            <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="searchQuery"
              type="search"
              :placeholder="t('conferences.search_placeholder')"
              class="input-base w-full pl-9 text-sm"
            />
          </div>
        </div>

        <!-- Year -->
        <div>
          <label class="mb-1 block text-[11px] font-semibold uppercase tracking-wider text-slate-500">{{ t('conferences.filter_year') }}</label>
          <div class="flex flex-wrap gap-1">
            <button
              class="rounded-md px-2.5 py-1.5 text-xs font-medium transition"
              :class="!yearFilter
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                : 'bg-stone-100 text-slate-600 hover:bg-stone-200 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-slate-600'"
              @click="yearFilter = ''"
            >{{ t('common.all') }}</button>
            <button
              v-for="y in years"
              :key="y"
              class="rounded-md px-2.5 py-1.5 text-xs font-medium transition"
              :class="yearFilter === String(y)
                ? 'bg-primary-100 text-primary-800 dark:bg-primary-950 dark:text-primary-300'
                : 'bg-stone-100 text-slate-600 hover:bg-stone-200 dark:bg-slate-700 dark:text-slate-400 dark:hover:bg-slate-600'"
              @click="yearFilter = String(y)"
            >{{ y }}</button>
          </div>
        </div>

        <!-- Clear (if filters active) -->
        <button
          v-if="searchQuery || yearFilter"
          class="flex items-center gap-1 rounded-lg bg-red-50 px-3 py-2 text-xs font-semibold text-red-600 transition hover:bg-red-100 dark:bg-red-950/30 dark:text-red-400 dark:hover:bg-red-950/50"
          @click="searchQuery = ''; yearFilter = ''"
        >
          <X :size="12" />
          {{ t('common.clear') }}
        </button>
      </div>
    </div>

    <div>
      <div v-if="loading" class="flex justify-center py-20">
        <AppSpinner :size="36" class="text-primary-500" />
      </div>

      <div v-else-if="!filtered.length" class="py-20 text-center">
        <FileText :size="48" class="mx-auto text-slate-200 dark:text-slate-700" />
        <p class="mt-4 text-slate-400">{{ t('conferences.no_results') }}</p>
      </div>

      <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="conf in filtered"
          :key="conf.id"
          :to="`/conferences/${conf.id}`"
          class="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:border-primary-300 hover:shadow-md dark:border-slate-700 dark:bg-slate-800 dark:hover:border-primary-700"
        >
          <!-- Cover image -->
          <div v-if="conf.cover_image_url" class="mb-4 overflow-hidden rounded-xl">
            <img
              :src="conf.cover_image_url.startsWith('/') ? conf.cover_image_url : `/api/uploads/${conf.cover_image_url}`"
              :alt="getLocalizedField(conf.title, localeStore.current, '')"
              class="h-40 w-full object-cover transition group-hover:scale-105"
            />
          </div>

          <h3 class="font-serif text-lg font-bold text-slate-900 group-hover:text-primary-700 dark:text-white dark:group-hover:text-primary-400">
            {{ getLocalizedField(conf.title, localeStore.current, '') }}
          </h3>

          <div class="mt-3 space-y-2 text-sm text-slate-500 dark:text-slate-400">
            <div v-if="conf.location" class="flex items-center gap-2">
              <MapPin :size="14" class="shrink-0" />
              <span>{{ conf.location }}</span>
            </div>
            <div v-if="conf.start_date" class="flex items-center gap-2">
              <Calendar :size="14" class="shrink-0" />
              <span>{{ conf.start_date }}{{ conf.end_date ? ` — ${conf.end_date}` : '' }}</span>
            </div>
            <div v-if="conf.organizer" class="flex items-center gap-2">
              <Users :size="14" class="shrink-0" />
              <span>{{ conf.organizer }}</span>
            </div>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <span class="rounded-full bg-primary-50 px-3 py-1 text-xs font-medium text-primary-700 dark:bg-primary-950 dark:text-primary-300">
              {{ conf.paper_count || 0 }} {{ t('conferences.papers') }}
            </span>
            <ChevronRight :size="16" class="text-slate-300 transition group-hover:translate-x-1 group-hover:text-primary-500" />
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
