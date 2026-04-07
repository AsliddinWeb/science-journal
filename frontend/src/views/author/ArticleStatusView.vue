<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  ChevronLeft, Download, ExternalLink, AlertCircle,
  RefreshCw, MessageSquare, UploadCloud, Send,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'
import ArticleTimeline from '@/components/article/ArticleTimeline.vue'
import PdfUploadZone from '@/components/upload/PdfUploadZone.vue'
import { formatDate } from '@/utils/formatDate'

interface ReviewForAuthor {
  id: string
  recommendation?: string | null
  comments_to_author?: string | null
  submitted_at?: string | null
}

interface ArticleDetail {
  id: string
  title: Record<string, string>
  abstract: Record<string, string>
  keywords: string[]
  doi?: string | null
  status: string
  language: string
  submission_date?: string | null
  published_date?: string | null
  pdf_file_path?: string | null
  volume_id?: string | null
  issue_id?: string | null
  reviews_for_author: ReviewForAuthor[]
}

const { t, locale } = useI18n()
const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()

const article = ref<ArticleDetail | null>(null)
const loading = ref(true)
const error = ref(false)

// Revision upload
const showRevision = ref(false)
const revPdfKey = ref<string | null>(null)
const revPdfName = ref<string | null>(null)
const revPdfSize = ref<number | null>(null)
const revCoverLetter = ref('')
const submittingRevision = ref(false)
const revisionError = ref('')
const revisionSuccess = ref(false)

const id = route.params.id as string

async function load() {
  loading.value = true
  error.value = false
  try {
    article.value = await api.get<ArticleDetail>(`/api/articles/${id}/status`)
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

const title = computed(() => {
  if (!article.value) return ''
  const titles = article.value.title
  return titles[localeStore.current] || titles.en || titles.ru || titles.uz || ''
})

const abstract = computed(() => {
  if (!article.value) return ''
  const abs = article.value.abstract
  return abs[localeStore.current] || abs.en || abs.ru || abs.uz || ''
})

async function submitRevision() {
  if (!revPdfKey.value) {
    revisionError.value = t('author.submit.validation.pdf_required')
    return
  }
  submittingRevision.value = true
  revisionError.value = ''
  try {
    await api.post(`/api/articles/${id}/revision`, {
      pdf_file_path: revPdfKey.value,
      pdf_file_size: revPdfSize.value,
      cover_letter: revCoverLetter.value || null,
    })
    revisionSuccess.value = true
    showRevision.value = false
    await load()
  } catch (e: any) {
    revisionError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    submittingRevision.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">

    <!-- Header -->
    <div class="border-b border-slate-200 bg-slate-50 py-6 dark:border-slate-800 dark:bg-slate-900">
      <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <button
          class="mb-3 flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-white"
          @click="router.back()"
        >
          <ChevronLeft :size="16" />{{ t('common.back') }}
        </button>

        <div v-if="article" class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <h1 class="font-serif text-xl font-bold text-slate-900 dark:text-white line-clamp-2">
              {{ title }}
            </h1>
            <p class="mt-1 text-sm text-slate-400">
              {{ t('articles.published') }}: {{ formatDate(article.submission_date, locale) }}
            </p>
          </div>
          <ArticleStatusBadge :status="(article.status as any)" />
        </div>

        <div v-else-if="loading" class="animate-pulse">
          <div class="h-6 w-2/3 rounded-lg bg-slate-200 dark:bg-slate-700" />
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="flex flex-col items-center py-20">
      <AlertCircle :size="40" class="text-red-400" />
      <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
    </div>

    <!-- Content -->
    <div v-else-if="article" class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_260px]">

        <!-- Main column -->
        <div class="space-y-6">

          <!-- Revision success banner -->
          <div
            v-if="revisionSuccess"
            class="flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 dark:border-green-900/50 dark:bg-green-950/20 dark:text-green-400"
          >
            <AlertCircle :size="16" />
            {{ t('author.articleStatus.revision_submitted') }}
          </div>

          <!-- Abstract -->
          <div class="card p-6">
            <h2 class="mb-3 font-serif text-base font-bold text-slate-900 dark:text-white">{{ t('article.abstract') }}</h2>
            <p class="text-sm leading-relaxed text-slate-600 dark:text-slate-400">{{ abstract }}</p>
          </div>

          <!-- Keywords -->
          <div v-if="article.keywords?.length" class="card p-5">
            <h2 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('article.keywords') }}</h2>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="kw in article.keywords"
                :key="kw"
                class="rounded-full bg-slate-100 px-3 py-1 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-400"
              >{{ kw }}</span>
            </div>
          </div>

          <!-- Reviewer comments (revision_required) -->
          <div v-if="article.reviews_for_author?.length" class="space-y-4">
            <h2 class="font-serif text-base font-bold text-slate-900 dark:text-white">
              {{ t('author.articleStatus.reviewer_comments') }}
            </h2>
            <div
              v-for="(review, i) in article.reviews_for_author"
              :key="review.id"
              class="card p-5"
            >
              <div class="mb-3 flex items-center gap-2">
                <MessageSquare :size="16" class="text-slate-400" />
                <span class="text-sm font-semibold text-slate-700 dark:text-slate-300">
                  {{ t('author.articleStatus.reviewer') }} {{ i + 1 }}
                </span>
                <span v-if="review.recommendation" class="rounded-full bg-amber-100 px-2 py-0.5 text-xs text-amber-700 dark:bg-amber-950 dark:text-amber-400">
                  {{ review.recommendation.replace('_', ' ') }}
                </span>
              </div>
              <p class="whitespace-pre-line text-sm leading-relaxed text-slate-600 dark:text-slate-400">
                {{ review.comments_to_author }}
              </p>
            </div>
          </div>

          <!-- Revision upload section -->
          <div v-if="article.status === 'revision_required'">
            <button
              v-if="!showRevision"
              class="btn-primary"
              @click="showRevision = true"
            >
              <UploadCloud :size="16" />{{ t('author.articleStatus.submit_revision') }}
            </button>

            <div v-else class="card space-y-4 p-6">
              <h3 class="font-serif text-base font-bold text-slate-900 dark:text-white">
                {{ t('author.articleStatus.submit_revision') }}
              </h3>
              <PdfUploadZone
                v-model="revPdfKey"
                v-model:file-name="revPdfName"
                v-model:file-size="revPdfSize"
              />
              <div>
                <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                  {{ t('author.submit.cover_letter') }}
                </label>
                <textarea
                  v-model="revCoverLetter"
                  rows="4"
                  class="input-base resize-none"
                  :placeholder="t('author.submit.cover_letter_placeholder')"
                />
              </div>
              <p v-if="revisionError" class="flex items-center gap-1.5 text-sm text-red-500">
                <AlertCircle :size="15" />{{ revisionError }}
              </p>
              <div class="flex gap-3">
                <button class="btn-primary" :disabled="submittingRevision" @click="submitRevision">
                  <Send v-if="!submittingRevision" :size="16" />
                  <RefreshCw v-else :size="16" class="animate-spin" />
                  {{ t('author.articleStatus.submit_revision') }}
                </button>
                <button class="btn-ghost" @click="showRevision = false">{{ t('common.cancel') }}</button>
              </div>
            </div>
          </div>

          <!-- Published info -->
          <div v-if="article.status === 'published'" class="card p-6 space-y-3">
            <h2 class="font-serif text-base font-bold text-slate-900 dark:text-white">
              {{ t('author.articleStatus.published_info') }}
            </h2>
            <div v-if="article.doi" class="flex items-center gap-2 text-sm">
              <span class="text-slate-500">DOI:</span>
              <a
                :href="`https://doi.org/${article.doi}`"
                target="_blank"
                rel="noopener noreferrer"
                class="text-primary-600 hover:underline dark:text-primary-400"
              >
                {{ article.doi }}<ExternalLink :size="12" class="ml-1 inline" />
              </a>
            </div>
            <div v-if="article.published_date" class="text-sm text-slate-500">
              {{ t('articles.published') }}: {{ formatDate(article.published_date, locale) }}
            </div>
            <div class="flex gap-3 pt-2">
              <router-link
                :to="{ name: 'article-detail', params: { id: article.id } }"
                class="btn-ghost text-sm"
              >
                <ExternalLink :size="14" />{{ t('author.articleStatus.view_on_site') }}
              </router-link>
              <a
                :href="`/api/articles/${article.id}/download`"
                target="_blank"
                class="btn-primary text-sm"
              >
                <Download :size="14" />{{ t('articles.download_pdf') }}
              </a>
            </div>
          </div>
        </div>

        <!-- Sidebar: Timeline -->
        <aside class="space-y-6">
          <div class="card p-5">
            <h3 class="mb-5 text-xs font-semibold uppercase tracking-wider text-slate-400">
              {{ t('author.articleStatus.timeline') }}
            </h3>
            <ArticleTimeline
              :status="(article.status as any)"
              :submission-date="article.submission_date"
              :published-date="article.published_date"
            />
          </div>

          <!-- Meta -->
          <div class="card divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden text-sm">
            <div class="flex justify-between p-4">
              <span class="text-slate-500">{{ t('articles.filter_language') }}</span>
              <span class="font-medium uppercase text-slate-700 dark:text-slate-300">{{ article.language }}</span>
            </div>
            <div v-if="article.pdf_file_path" class="p-4">
              <span class="text-slate-500">PDF</span>
              <span class="ml-2 text-green-600 dark:text-green-400">✓ {{ t('upload.uploadSuccess') }}</span>
            </div>
          </div>
        </aside>
      </div>
    </div>

    <!-- Loading skeleton -->
    <div v-else-if="loading" class="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_260px]">
        <div class="space-y-4 animate-pulse">
          <div class="h-32 rounded-2xl bg-slate-100 dark:bg-slate-800" />
          <div class="h-20 rounded-2xl bg-slate-100 dark:bg-slate-800" />
        </div>
        <div class="h-48 animate-pulse rounded-2xl bg-slate-100 dark:bg-slate-800" />
      </div>
    </div>
  </div>
</template>
