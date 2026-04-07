<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Calendar, MapPin, Users, Globe, FileText, Download, Eye,
  ChevronRight, AlertCircle, RefreshCw, ExternalLink
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { useSeoMeta } from '@/composables/useSeoMeta'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import PdfPreview from '@/components/ui/PdfPreview.vue'
import type { Conference, ConferencePaper } from '@/types/conference'
import type { PaginatedResponse } from '@/types/article'

const { t } = useI18n()
const route = useRoute()
const localeStore = useLocaleStore()
const { apply: applySeo } = useSeoMeta()

const conference = ref<Conference | null>(null)
const papers = ref<ConferencePaper[]>([])
const loading = ref(true)
const error = ref(false)
const activeSession = ref('')
const previewPaper = ref<ConferencePaper | null>(null)

const confId = computed(() => route.params.id as string)
const title = computed(() => conference.value ? getLocalizedField(conference.value.title, localeStore.current, '') : '')

const filteredPapers = computed(() => {
  if (!activeSession.value) return papers.value
  return papers.value.filter(p => p.session_id === activeSession.value)
})

async function load() {
  loading.value = true
  error.value = false
  try {
    const [conf, papersData] = await Promise.all([
      api.get<Conference>(`/api/conferences/${confId.value}`),
      api.get<PaginatedResponse<ConferencePaper>>(`/api/conferences/${confId.value}/papers?limit=100`),
    ])
    conference.value = conf
    papers.value = papersData.items
    applySeo({ title: getLocalizedField(conf.title, localeStore.current, '') })
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

async function downloadPaper(paper: ConferencePaper) {
  try {
    const { download_url } = await api.get<{ download_url: string }>(`/api/conferences/${confId.value}/papers/${paper.id}/download`)
    const a = document.createElement('a')
    a.href = download_url
    a.target = '_blank'
    a.click()
  } catch {
    if (paper.pdf_file_path) {
      const path = paper.pdf_file_path.startsWith('/') ? paper.pdf_file_path : `/api/uploads/${paper.pdf_file_path}`
      window.open(path, '_blank')
    }
  }
}

onMounted(load)
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <div v-if="loading" class="flex justify-center py-32">
      <AppSpinner :size="36" class="text-primary-500" />
    </div>

    <div v-else-if="error" class="flex flex-col items-center justify-center py-32">
      <AlertCircle :size="40" class="text-red-400" />
      <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
    </div>

    <template v-else-if="conference">
      <!-- Hero -->
      <div class="border-b border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-900">
        <div class="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
          <div class="flex flex-col gap-6 lg:flex-row lg:items-start lg:gap-10">
            <!-- Cover image -->
            <div v-if="conference.cover_image_url" class="shrink-0 overflow-hidden rounded-2xl lg:w-72">
              <img
                :src="conference.cover_image_url.startsWith('/') ? conference.cover_image_url : `/api/uploads/${conference.cover_image_url}`"
                :alt="title"
                class="h-48 w-full object-cover lg:h-56"
              />
            </div>

            <div class="flex-1">
              <h1 class="font-serif text-3xl font-bold text-slate-900 dark:text-white">{{ title }}</h1>

              <div class="mt-4 flex flex-wrap gap-4 text-sm text-slate-500 dark:text-slate-400">
                <span v-if="conference.location" class="flex items-center gap-1.5">
                  <MapPin :size="15" /> {{ conference.location }}
                </span>
                <span v-if="conference.start_date" class="flex items-center gap-1.5">
                  <Calendar :size="15" /> {{ conference.start_date }}{{ conference.end_date ? ` — ${conference.end_date}` : '' }}
                </span>
                <span v-if="conference.organizer" class="flex items-center gap-1.5">
                  <Users :size="15" /> {{ conference.organizer }}
                </span>
              </div>

              <p v-if="conference.description" class="mt-4 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
                {{ getLocalizedField(conference.description, localeStore.current, '') }}
              </p>

              <a
                v-if="conference.website_url"
                :href="conference.website_url"
                target="_blank"
                rel="noopener noreferrer"
                class="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-primary-600 hover:underline dark:text-primary-400"
              >
                <ExternalLink :size="14" /> {{ t('conferences.website') }}
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- Content -->
      <div class="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <!-- Session filter tabs -->
        <div v-if="conference.sessions.length" class="mb-6">
          <div class="flex flex-wrap gap-2">
            <button
              class="rounded-lg px-4 py-2 text-sm font-medium transition"
              :class="!activeSession
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
              @click="activeSession = ''"
            >
              {{ t('common.all') }} ({{ papers.length }})
            </button>
            <button
              v-for="sess in conference.sessions"
              :key="sess.id"
              class="rounded-lg px-4 py-2 text-sm font-medium transition"
              :class="activeSession === sess.id
                ? 'bg-primary-600 text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300'"
              @click="activeSession = sess.id"
            >
              {{ getLocalizedField(sess.title, localeStore.current, '') }}
            </button>
          </div>
        </div>

        <!-- Papers -->
        <div v-if="!filteredPapers.length" class="py-16 text-center text-slate-400">
          <FileText :size="48" class="mx-auto text-slate-200 dark:text-slate-700" />
          <p class="mt-4">{{ t('conferences.no_papers') }}</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="paper in filteredPapers"
            :key="paper.id"
            class="rounded-xl border border-slate-200 bg-white p-5 transition hover:border-primary-200 hover:shadow-sm dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <h3 class="font-serif text-base font-bold text-slate-900 dark:text-white">
                  {{ getLocalizedField(paper.title, localeStore.current, '') }}
                </h3>
                <p v-if="paper.author" class="mt-1 text-sm text-slate-500 dark:text-slate-400">
                  {{ paper.author.full_name }}
                  <template v-if="paper.co_authors?.length"> + {{ paper.co_authors.length }}</template>
                </p>
                <p class="mt-2 text-sm leading-relaxed text-slate-600 line-clamp-2 dark:text-slate-300">
                  {{ getLocalizedField(paper.abstract, localeStore.current, '') }}
                </p>
                <div v-if="paper.keywords?.length" class="mt-2 flex flex-wrap gap-1.5">
                  <span
                    v-for="kw in paper.keywords.slice(0, 5)"
                    :key="kw"
                    class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-500 dark:bg-slate-700 dark:text-slate-400"
                  >{{ kw }}</span>
                </div>
              </div>
              <div class="flex shrink-0 flex-col gap-2">
                <button
                  v-if="paper.pdf_file_path"
                  class="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-2 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950 dark:text-primary-300"
                  @click="previewPaper = paper"
                >
                  <Eye :size="13" /> PDF
                </button>
                <button
                  v-if="paper.pdf_file_path"
                  class="flex items-center gap-1.5 rounded-lg bg-slate-100 px-2 py-2 text-xs text-slate-500 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-400"
                  @click="downloadPaper(paper)"
                >
                  <Download :size="13" />
                </button>
                <div class="flex items-center gap-3 text-xs text-slate-400">
                  <span class="flex items-center gap-1"><Eye :size="12" /> {{ paper.view_count }}</span>
                  <span class="flex items-center gap-1"><Download :size="12" /> {{ paper.download_count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <PdfPreview
      v-if="previewPaper?.pdf_file_path"
      :url="previewPaper.pdf_file_path.startsWith('/') ? previewPaper.pdf_file_path : `/api/uploads/${previewPaper.pdf_file_path}`"
      :title="previewPaper.title.uz || previewPaper.title.en || previewPaper.title.ru || 'PDF'"
      @close="previewPaper = null"
    />
  </div>
</template>
