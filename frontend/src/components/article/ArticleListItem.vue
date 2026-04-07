<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Eye, Download, ExternalLink, Calendar, Globe } from 'lucide-vue-next'
import type { Article } from '@/types/article'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'

const props = defineProps<{
  article: Article
  volumeNumber?: number
  issueNumber?: number
  highlightQuery?: string
}>()

const { t } = useI18n()
const localeStore = useLocaleStore()

const title = computed(() =>
  getLocalizedField(props.article.title, localeStore.current, t('common.no_data'))
)
const abstract = computed(() =>
  getLocalizedField(props.article.abstract, localeStore.current, '')
)

const langMap: Record<string, string> = { uz: "O'zbek", ru: 'Русский', en: 'English' }
const langLabel = computed(() => langMap[props.article.language] ?? props.article.language.toUpperCase())

const mainAuthorName = computed(() => props.article.author?.full_name ?? '')
const coAuthors = computed(() => props.article.co_authors ?? [])

function highlight(text: string): string {
  if (!props.highlightQuery || !text) return text
  const escaped = props.highlightQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(new RegExp(`(${escaped})`, 'gi'), '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded">$1</mark>')
}
</script>

<template>
  <article class="card p-5 transition-shadow hover:shadow-md">
    <!-- Header row -->
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="flex flex-wrap items-center gap-2">
        <span class="badge bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
          <Globe :size="10" class="mr-0.5" />
          {{ langLabel }}
        </span>
        <span
          v-if="volumeNumber && issueNumber"
          class="badge bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
        >
          Vol.{{ volumeNumber }} №{{ issueNumber }}
        </span>
      </div>
      <span
        v-if="article.published_date"
        class="flex items-center gap-1 text-xs text-slate-400 dark:text-slate-500"
      >
        <Calendar :size="12" />
        {{ formatDateShort(article.published_date) }}
      </span>
    </div>

    <!-- Title -->
    <h3 class="mt-3 font-serif text-lg font-semibold leading-snug text-slate-900 dark:text-white">
      <RouterLink
        :to="`/articles/${article.id}`"
        class="hover:text-primary-600 dark:hover:text-primary-400"
        v-html="highlight(title)"
      />
    </h3>

    <!-- Authors -->
    <p class="mt-1.5 text-sm text-slate-500 dark:text-slate-400">
      {{ mainAuthorName }}
      <template v-if="coAuthors.length">
        <span v-for="(ca, i) in coAuthors.slice(0, 3)" :key="ca.id">
          , {{ ca.user?.full_name ?? ca.guest_name }}
        </span>
        <span v-if="coAuthors.length > 3"> +{{ coAuthors.length - 3 }} {{ t('article.more_authors') }}</span>
      </template>
    </p>

    <!-- Abstract -->
    <p class="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600 dark:text-slate-400" v-html="highlight(abstract)" />

    <!-- DOI -->
    <a
      v-if="article.doi"
      :href="`https://doi.org/${article.doi}`"
      target="_blank"
      rel="noopener noreferrer"
      class="mt-2 inline-flex items-center gap-1 text-xs text-slate-400 hover:text-primary-600 dark:hover:text-primary-400"
    >
      <ExternalLink :size="11" />
      DOI: {{ article.doi }}
    </a>

    <!-- Footer -->
    <div class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-4 dark:border-slate-700">
      <div class="flex items-center gap-4 text-xs text-slate-400 dark:text-slate-500">
        <span class="flex items-center gap-1">
          <Eye :size="13" />
          {{ article.view_count.toLocaleString() }} {{ t('articles.views') }}
        </span>
        <span class="flex items-center gap-1">
          <Download :size="13" />
          {{ article.download_count.toLocaleString() }} {{ t('articles.downloads') }}
        </span>
      </div>
      <div class="flex items-center gap-2">
        <RouterLink :to="`/articles/${article.id}`" class="btn-ghost px-3 py-1.5 text-xs">
          {{ t('articles.view') }}
        </RouterLink>
        <a
          v-if="article.pdf_file_path"
          :href="`/api/articles/${article.id}/download`"
          target="_blank"
          rel="noopener noreferrer"
          class="btn-secondary px-3 py-1.5 text-xs"
        >
          <Download :size="13" />
          {{ t('articles.download_pdf') }}
        </a>
      </div>
    </div>
  </article>
</template>
