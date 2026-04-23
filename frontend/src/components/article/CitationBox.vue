<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Copy, Check } from 'lucide-vue-next'
import type { Article } from '@/types/article'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'

const props = defineProps<{ article: Article }>()

const { t } = useI18n()
const localeStore = useLocaleStore()

type Tab = 'apa' | 'mla' | 'bibtex'
const activeTab = ref<Tab>('apa')
const copied = ref(false)

// Title in the article's own primary language — independent of UI locale.
const title = computed(() =>
  getLocalizedField(props.article.title, props.article.language, 'Untitled')
)

const authors = computed(() => {
  const main = props.article.author?.full_name ?? 'Unknown Author'
  const coNames = (props.article.co_authors ?? []).map(
    (a) => a.user?.full_name ?? a.guest_name ?? ''
  ).filter(Boolean)
  return [main, ...coNames]
})

const year = computed(() =>
  props.article.published_date
    ? new Date(props.article.published_date).getFullYear()
    : new Date().getFullYear()
)

const UZ_AP = '[\\u02BB\\u02BC\\u2018\\u2019\\x27\\x60\\xB4]'
const UZ_PATRONYMIC = new RegExp(
  `^(o${UZ_AP}?g${UZ_AP}?li|og${UZ_AP}?li|ogli|qizi|qız[ıi])$`,
  'i',
)
function scholarName(fullName: string): string {
  const raw = fullName.trim().split(/\s+/).filter(Boolean)
  if (raw.length < 2) return fullName.trim()
  const patronymic: string[] = []
  const parts = [...raw]
  while (parts.length > 1 && UZ_PATRONYMIC.test(parts[parts.length - 1])) {
    patronymic.unshift(parts.pop() as string)
  }
  if (parts.length < 2) return fullName.trim()
  let last: string
  let givens: string[]
  if (patronymic.length > 0) {
    last = parts[0]; givens = parts.slice(1)
  } else {
    last = parts[parts.length - 1]; givens = parts.slice(0, -1)
  }
  const initials = givens.map(p => p.charAt(0).toUpperCase() + '.').join(' ')
  const tail = patronymic.length ? ` ${patronymic.join(' ')}` : ''
  return initials ? `${last}, ${initials}${tail}` : `${last}${tail}`
}

const apa = computed(() => {
  const authorStr = authors.value.map(scholarName).join(', & ')
  const doi = props.article.doi ? ` https://doi.org/${props.article.doi}` : ''
  return `${authorStr} (${year.value}). ${title.value}.${doi}`
})

const mla = computed(() => {
  const [first, ...rest] = authors.value
  const authorStr = rest.length ? `${first}, et al.` : first
  const doi = props.article.doi ? ` doi:${props.article.doi}` : ''
  return `${authorStr}. "${title.value}." ${year.value}.${doi}`
})

const bibtex = computed(() => {
  const key = (authors.value[0]?.split(' ').pop() ?? 'Author') + year.value
  const authorStr = authors.value.join(' and ')
  const doi = props.article.doi ? `\n  doi = {${props.article.doi}},` : ''
  return `@article{${key},\n  author = {${authorStr}},\n  title = {${title.value}},\n  year = {${year.value}},${doi}\n}`
})

const currentCitation = computed(() => {
  if (activeTab.value === 'apa') return apa.value
  if (activeTab.value === 'mla') return mla.value
  return bibtex.value
})

async function copy() {
  await navigator.clipboard.writeText(currentCitation.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

const tabs: { key: Tab; label: string }[] = [
  { key: 'apa', label: 'APA' },
  { key: 'mla', label: 'MLA' },
  { key: 'bibtex', label: 'BibTeX' },
]
</script>

<template>
  <div class="rounded-xl border border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
    <!-- Tab bar -->
    <div class="flex border-b border-slate-200 dark:border-slate-700">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="px-4 py-2.5 text-xs font-semibold transition-colors"
        :class="activeTab === tab.key
          ? 'border-b-2 border-primary-600 text-primary-700 dark:border-primary-400 dark:text-primary-300'
          : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Citation text -->
    <div class="relative p-4">
      <pre class="whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-300 font-sans">{{ currentCitation }}</pre>
      <button
        class="absolute right-3 top-3 flex items-center gap-1 rounded-lg bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 shadow-sm transition-colors hover:bg-primary-50 hover:text-primary-700 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-primary-950 dark:hover:text-primary-300"
        @click="copy"
      >
        <Check v-if="copied" :size="13" class="text-green-500" />
        <Copy v-else :size="13" />
        {{ copied ? t('article.copied') : t('article.copy_citation') }}
      </button>
    </div>
  </div>
</template>
