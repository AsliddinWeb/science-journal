<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookOpen, ChevronDown, ChevronRight, Calendar, FileText, AlertCircle, RefreshCw } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import CoverImage from '@/components/ui/CoverImage.vue'
import type { Volume } from '@/types/volume'
import { formatDateShort } from '@/utils/formatDate'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()

useSeoMeta({
  title: t('nav.archive') || 'Archive',
  canonical: `${window.location.origin}/archive`,
  ogUrl: `${window.location.origin}/archive`,
})
const volumes = ref<Volume[]>([])
const loading = ref(true)
const error = ref(false)
const expandedVolumes = ref<Set<string>>(new Set())

async function load() {
  loading.value = true
  error.value = false
  try {
    volumes.value = await api.get<Volume[]>('/api/volumes')
    // auto-expand current volume
    const current = volumes.value.find((v) => v.is_current)
    if (current) expandedVolumes.value.add(current.id)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

function toggleVolume(id: string) {
  if (expandedVolumes.value.has(id)) expandedVolumes.value.delete(id)
  else expandedVolumes.value.add(id)
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <div class="flex items-center gap-3">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-primary-500/20 backdrop-blur">
          <BookOpen :size="22" class="text-primary-300" />
        </div>
        <div>
          <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('archive.title') }}</h1>
          <p class="text-sm text-slate-300">{{ t('archive.subtitle', { count: volumes.length }) }}</p>
        </div>
      </div>
    </section>

    <div>

      <!-- Error -->
      <div v-if="error" class="flex flex-col items-center justify-center py-24">
        <AlertCircle :size="40" class="text-red-400" />
        <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
        <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
      </div>

      <!-- Skeleton -->
      <div v-else-if="loading" class="space-y-3">
        <div v-for="i in 4" :key="i" class="card animate-pulse p-5">
          <div class="flex justify-between">
            <div class="h-6 w-40 rounded-lg bg-slate-200 dark:bg-slate-700" />
            <div class="h-6 w-24 rounded-full bg-slate-200 dark:bg-slate-700" />
          </div>
          <div class="mt-2 h-4 w-32 rounded bg-slate-100 dark:bg-slate-800" />
        </div>
      </div>

      <!-- Empty -->
      <div v-else-if="volumes.length === 0" class="flex flex-col items-center justify-center py-24">
        <BookOpen :size="48" class="text-slate-200 dark:text-slate-700" />
        <p class="mt-4 text-slate-400">{{ t('archive.no_volumes') }}</p>
      </div>

      <!-- Volumes list -->
      <div v-else class="space-y-3">
        <div
          v-for="volume in volumes"
          :key="volume.id"
          class="card overflow-hidden"
        >
          <!-- Volume header (clickable) -->
          <button
            class="flex w-full items-center justify-between px-5 py-4 text-left transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50"
            @click="toggleVolume(volume.id)"
          >
            <div class="flex items-center gap-4">
              <CoverImage
                :src="volume.cover_image_url"
                :alt="`Jild ${volume.number} (${volume.year})`"
                height="h-12 w-12"
                rounded="rounded-lg"
              />
              <div>
                <div class="flex items-center gap-2">
                  <h2 class="font-serif text-lg font-semibold text-slate-900 dark:text-white">
                    {{ t('archive.volume_label', { number: volume.number, year: volume.year }) }}
                  </h2>
                  <span
                    v-if="volume.is_current"
                    class="badge bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400"
                  >
                    {{ t('archive.current') }}
                  </span>
                </div>
                <p class="text-sm text-slate-500 dark:text-slate-400">
                  {{ volume.issues.length }} {{ t('archive.issues_count') }}
                </p>
              </div>
            </div>
            <ChevronDown
              :size="20"
              class="shrink-0 text-slate-400 transition-transform"
              :class="{ 'rotate-180': expandedVolumes.has(volume.id) }"
            />
          </button>

          <!-- Issues list (expanded) -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            leave-active-class="transition-all duration-150 ease-in"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="expandedVolumes.has(volume.id)" class="border-t border-slate-100 dark:border-slate-800">
              <div v-if="volume.issues.length === 0" class="px-5 py-4 text-sm text-slate-400">
                {{ t('archive.no_issues') }}
              </div>
              <RouterLink
                v-for="issue in volume.issues"
                :key="issue.id"
                :to="`/archive/${volume.id}/issues/${issue.id}`"
                class="flex items-center justify-between px-5 py-3.5 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800/50 group"
              >
                <div class="flex items-center gap-3">
                  <CoverImage
                    :src="issue.cover_image_url"
                    :alt="`Son ${issue.number}`"
                    height="h-12 w-12"
                    rounded="rounded-lg"
                  />
                  <div>
                    <p class="font-medium text-slate-700 transition-colors group-hover:text-primary-600 dark:text-slate-300 dark:group-hover:text-primary-400">
                      {{ t('archive.issue_label', { number: issue.number }) }}
                    </p>
                    <div class="flex items-center gap-3 text-xs text-slate-400 dark:text-slate-500">
                      <span v-if="issue.published_date" class="flex items-center gap-1">
                        <Calendar :size="11" />
                        {{ formatDateShort(issue.published_date) }}
                      </span>
                      <span class="flex items-center gap-1">
                        <FileText :size="11" />
                        {{ issue.article_count }} {{ t('archive.articles') }}
                      </span>
                    </div>
                  </div>
                </div>
                <ChevronRight :size="16" class="text-slate-300 transition-colors group-hover:text-primary-500 dark:text-slate-600" />
              </RouterLink>
            </div>
          </Transition>
        </div>
      </div>
    </div>
  </div>
</template>
