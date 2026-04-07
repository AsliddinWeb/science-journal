<script setup lang="ts">
import { computed } from 'vue'
import { FileText } from 'lucide-vue-next'
import type { Article } from '@/types/article'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'

const props = defineProps<{
  article: Article
}>()

const localeStore = useLocaleStore()

const title = computed(() =>
  getLocalizedField(props.article.title, localeStore.current, 'Untitled')
)

const authorsText = computed(() => {
  const main = props.article.author?.full_name || ''
  const co = (props.article.co_authors || []).map(c => c.guest_name || c.user?.full_name).filter(Boolean)
  return [main, ...co].join(', ')
})
</script>

<template>
  <RouterLink
    :to="`/articles/${article.id}`"
    class="group block rounded-xl border border-stone-200 bg-white p-5 transition hover:border-primary-400 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
  >
    <h3 class="font-serif text-base font-bold leading-snug text-journal-800 transition group-hover:text-primary-700 dark:text-slate-200 dark:group-hover:text-primary-400">
      {{ title }}
    </h3>
    <p class="mt-1.5 text-sm text-slate-600 dark:text-slate-400">{{ authorsText }}</p>

    <div v-if="article.doi" class="mt-3 flex items-center gap-2 text-xs text-primary-700 dark:text-primary-400">
      <span class="h-4 w-4 rounded-full bg-primary-500 flex-shrink-0" />
      <span class="truncate font-mono">https://doi.org/{{ article.doi }}</span>
    </div>

    <div class="mt-3 flex items-center gap-2">
      <span
        v-if="article.pdf_file_path"
        class="inline-flex items-center gap-1.5 rounded-md bg-primary-100 px-3 py-1.5 text-xs font-semibold text-primary-800 dark:bg-primary-950 dark:text-primary-300"
      >
        <FileText :size="12" />
        Full text (PDF)
      </span>
      <span v-if="article.published_date" class="ml-auto text-xs text-slate-400">
        {{ new Date(article.published_date).getFullYear() }}
      </span>
    </div>
  </RouterLink>
</template>
