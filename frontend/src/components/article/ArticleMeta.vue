<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ExternalLink, Calendar, BookOpen, Globe } from 'lucide-vue-next'
import type { Article } from '@/types/article'
import { formatDateShort } from '@/utils/formatDate'

const props = defineProps<{
  article: Article
  volumeNumber?: number
  issueNumber?: number
}>()

const { t } = useI18n()

const langLabel = computed(() => {
  const map: Record<string, string> = { uz: "O'zbek", ru: 'Русский', en: 'English' }
  return map[props.article.language] ?? props.article.language.toUpperCase()
})
</script>

<template>
  <div class="flex flex-wrap items-center gap-2 text-xs">
    <!-- Language badge -->
    <span class="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-1 font-medium text-primary-700 dark:bg-primary-950 dark:text-primary-300">
      <Globe :size="11" />
      {{ langLabel }}
    </span>

    <!-- Volume/Issue badge -->
    <span
      v-if="volumeNumber && issueNumber"
      class="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-300"
    >
      <BookOpen :size="11" />
      {{ t('articles.volume_issue', { vol: volumeNumber, issue: issueNumber }) }}
    </span>

    <!-- Published date -->
    <span
      v-if="article.published_date"
      class="inline-flex items-center gap-1 text-slate-500 dark:text-slate-400"
    >
      <Calendar :size="11" />
      {{ formatDateShort(article.published_date) }}
    </span>

    <!-- DOI -->
    <a
      v-if="article.doi"
      :href="`https://doi.org/${article.doi}`"
      target="_blank"
      rel="noopener noreferrer"
      class="inline-flex items-center gap-1 text-slate-500 hover:text-primary-600 dark:text-slate-400 dark:hover:text-primary-400"
    >
      <ExternalLink :size="11" />
      {{ article.doi }}
    </a>
  </div>
</template>
