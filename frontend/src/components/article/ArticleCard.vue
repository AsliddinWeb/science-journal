<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { BadgeCheck, Calendar, Eye, Download, BookOpen } from 'lucide-vue-next'
import type { Article } from '@/types/article'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'

const props = defineProps<{
  article: Article
  highlightQuery?: string
}>()

const { t } = useI18n()
const localeStore = useLocaleStore()

const title = computed(() =>
  getLocalizedField(props.article.title, localeStore.current, 'Untitled')
)
const abstract = computed(() =>
  getLocalizedField(props.article.abstract, localeStore.current, '')
)

const UPLOADER_ROLES = new Set(['superadmin'])

const authorsText = computed(() => {
  const names: string[] = []
  const a = props.article.author
  if (a?.full_name && !UPLOADER_ROLES.has(a.role)) names.push(a.full_name)
  ;(props.article.co_authors ?? []).forEach((c) => {
    const n = c.user?.full_name || c.guest_name
    if (n) names.push(n)
  })
  return names.join(', ')
})

const volIssueLabel = computed(() => {
  const v = props.article.volume
  const i = props.article.issue
  if (!v) return ''
  return i ? `Volume ${v.number} Issue ${i.number}` : `Volume ${v.number}`
})

function highlight(text: string): string {
  if (!props.highlightQuery || !text) return text
  const escaped = props.highlightQuery.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  return text.replace(
    new RegExp(`(${escaped})`, 'gi'),
    '<mark class="bg-yellow-200 dark:bg-yellow-800 rounded px-0.5">$1</mark>',
  )
}

const downloadHref = computed(() => {
  const p = props.article.pdf_file_path
  if (!p) return ''
  return p.startsWith('http') || p.startsWith('/') ? p : `/api/uploads/${p}`
})
</script>

<template>
  <article class="group overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:border-primary-400 hover:shadow-md dark:border-slate-700 dark:bg-slate-800">
    <!-- Header: title + accent icon -->
    <RouterLink
      :to="`/articles/${article.id}`"
      class="block border-b border-slate-200 bg-slate-50 px-5 py-3 dark:border-slate-700 dark:bg-slate-800/60"
    >
      <h3
        class="flex items-start gap-2 font-serif text-sm font-semibold leading-snug text-primary-700 transition group-hover:text-primary-800 dark:text-primary-300 dark:group-hover:text-primary-200 sm:text-base"
      >
        <BadgeCheck :size="18" class="mt-0.5 shrink-0 text-primary-500" />
        <span v-html="highlight(title)" />
      </h3>
    </RouterLink>

    <div class="px-5 pb-4 pt-3">
      <!-- Authors -->
      <p v-if="authorsText" class="mb-2 font-serif text-[15px] font-semibold text-slate-900 dark:text-slate-100">
        {{ authorsText }}
      </p>

      <!-- Abstract -->
      <p
        v-if="abstract"
        class="line-clamp-4 text-sm leading-relaxed text-slate-600 dark:text-slate-300"
        v-html="highlight(abstract)"
      />

      <!-- Badges row -->
      <div class="mt-4 flex flex-wrap items-center gap-2">
        <span
          v-if="article.published_date"
          class="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2.5 py-1 text-[11px] font-medium text-white dark:bg-slate-900"
        >
          <Calendar :size="11" />
          {{ formatDateShort(article.published_date) }}
        </span>

        <span
          v-if="volIssueLabel"
          class="inline-flex items-center gap-1 rounded-md bg-slate-800 px-2.5 py-1 text-[11px] font-medium text-white dark:bg-slate-900"
        >
          <BookOpen :size="11" />
          {{ volIssueLabel }}
        </span>

        <RouterLink
          :to="`/articles/${article.id}`"
          class="inline-flex items-center gap-1 rounded-md bg-sky-500 px-2.5 py-1 text-[11px] font-semibold text-white transition hover:bg-sky-600"
        >
          <Eye :size="11" />
          {{ t('articles.view') }}
        </RouterLink>

        <a
          v-if="downloadHref"
          :href="downloadHref"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-1 rounded-md bg-emerald-500 px-2.5 py-1 text-[11px] font-semibold text-white transition hover:bg-emerald-600"
        >
          <Download :size="11" />
          {{ t('articles.download_pdf') }}
        </a>

        <a
          v-if="article.doi"
          :href="`https://doi.org/${article.doi}`"
          target="_blank"
          rel="noopener noreferrer"
          :title="`https://doi.org/${article.doi}`"
          class="inline-flex h-[22px] w-[22px] items-center justify-center rounded bg-[#fcb425] text-[10px] font-black text-white transition hover:bg-[#e29b0b]"
        >
          DOI
        </a>

        <!-- Footer view stats (right-aligned) -->
        <span class="ml-auto flex items-center gap-3 text-[11px] text-slate-400 dark:text-slate-500">
          <span class="inline-flex items-center gap-1"><Eye :size="11" />{{ article.view_count.toLocaleString() }}</span>
          <span class="inline-flex items-center gap-1"><Download :size="11" />{{ article.download_count.toLocaleString() }}</span>
        </span>
      </div>
    </div>
  </article>
</template>
