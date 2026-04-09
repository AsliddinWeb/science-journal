<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { AlertCircle, RefreshCw, FileText, ChevronRight } from 'lucide-vue-next'
import { marked } from 'marked'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { useSeoMeta } from '@/composables/useSeoMeta'

marked.setOptions({ breaks: true, gfm: true })

interface StaticPage {
  id: string
  slug: string
  title_uz: string
  title_ru: string
  title_en: string
  content_uz?: string
  content_ru?: string
  content_en?: string
  is_published: boolean
}

const { t, locale } = useI18n()
const route = useRoute()
const localeStore = useLocaleStore()
const { apply: applySeo } = useSeoMeta()

const page = ref<StaticPage | null>(null)
const loading = ref(true)
const error = ref(false)
const contentEl = ref<HTMLElement | null>(null)

interface TocItem { id: string; text: string; level: number }
const toc = ref<TocItem[]>([])
const activeId = ref('')

const slug = computed(() => route.params.slug as string)

const title = computed(() => {
  if (!page.value) return ''
  const map: Record<string, string> = {
    uz: page.value.title_uz,
    ru: page.value.title_ru,
    en: page.value.title_en,
  }
  return map[localeStore.current] ?? page.value.title_en
})

const rawContent = computed(() => {
  if (!page.value) return ''
  const map: Record<string, string | undefined> = {
    uz: page.value.content_uz,
    ru: page.value.content_ru,
    en: page.value.content_en,
  }
  return map[localeStore.current] ?? page.value.content_en ?? ''
})

const content = computed(() => {
  try { return marked.parse(rawContent.value || '') as string } catch { return '' }
})

async function load() {
  loading.value = true
  error.value = false
  toc.value = []
  try {
    page.value = await api.get<StaticPage>(`/api/pages/${slug.value}`)
    const pageTitle = page.value.title_en || page.value.title_uz
    const pageContent = page.value.content_en || page.value.content_uz || ''
    applySeo({
      title: pageTitle,
      description: pageContent.replace(/#.+\n|^\s+/gm, '').slice(0, 160),
      canonical: `https://scientists.uz/pages/${slug.value}`,
      ogUrl: `https://scientists.uz/pages/${slug.value}`,
    })
    await nextTick()
    buildToc()
    setupObserver()
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

function buildToc() {
  if (!contentEl.value) return
  const headings = contentEl.value.querySelectorAll('h2, h3')
  toc.value = Array.from(headings).map((el, i) => {
    const id = `section-${i}`
    el.id = id
    return {
      id,
      text: (el as HTMLElement).innerText,
      level: el.tagName === 'H2' ? 2 : 3,
    }
  })
}

let observer: IntersectionObserver | null = null
function setupObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) activeId.value = entry.target.id
      }
    },
    { rootMargin: '-20% 0% -70% 0%' }
  )
  if (!contentEl.value) return
  contentEl.value.querySelectorAll('h2, h3').forEach((el) => observer!.observe(el))
}

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(load)
watch(slug, load)
watch(locale, () => nextTick(buildToc))
</script>

<template>
  <div class="space-y-6">

    <!-- Error -->
    <div v-if="error" class="flex flex-col items-center justify-center py-32">
      <AlertCircle :size="40" class="text-red-400" />
      <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
      <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
    </div>

    <!-- Header skeleton -->
    <div v-else-if="loading" class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <div class="h-8 w-64 animate-pulse rounded-lg bg-white/10" />
    </div>

    <template v-else-if="page">
      <!-- Breadcrumb -->
      <nav class="flex items-center gap-1.5 text-sm text-slate-500 dark:text-slate-400">
        <RouterLink to="/" class="hover:text-primary-700 dark:hover:text-primary-300">{{ t('nav.home') }}</RouterLink>
        <ChevronRight :size="14" />
        <span class="text-journal-800 dark:text-primary-300">{{ title }}</span>
      </nav>

      <!-- Title -->
      <div class="border-b-2 border-primary-400 pb-4">
        <h1 class="font-serif text-3xl font-bold text-slate-900 dark:text-white sm:text-4xl">{{ title }}</h1>
      </div>

      <div class="grid gap-8 lg:grid-cols-[1fr_220px]">
        <!-- Content -->
        <article
          ref="contentEl"
          class="prose prose-slate max-w-none min-w-0 dark:prose-invert
            prose-headings:font-serif prose-headings:font-bold prose-headings:text-journal-800 dark:prose-headings:text-primary-300
            prose-h1:text-3xl prose-h1:border-b prose-h1:border-primary-200 prose-h1:pb-3 prose-h1:mb-6
            prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4
            prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
            prose-p:text-slate-700 prose-p:leading-relaxed dark:prose-p:text-slate-300
            prose-a:text-primary-600 dark:prose-a:text-primary-400 prose-a:font-medium prose-a:no-underline hover:prose-a:underline
            prose-strong:text-journal-800 dark:prose-strong:text-slate-100
            prose-blockquote:border-primary-400 prose-blockquote:bg-stone-50 dark:prose-blockquote:bg-slate-800 prose-blockquote:rounded-r-lg prose-blockquote:py-2 prose-blockquote:not-italic
            prose-code:bg-stone-100 prose-code:text-primary-700 prose-code:rounded prose-code:px-1.5 prose-code:py-0.5 prose-code:before:content-none prose-code:after:content-none dark:prose-code:bg-slate-900
            prose-img:rounded-xl prose-img:shadow-md
            prose-hr:border-stone-200 dark:prose-hr:border-slate-700
            prose-ul:space-y-1 prose-li:text-slate-700 dark:prose-li:text-slate-300
            prose-ol:space-y-1"
          v-html="content"
        />

        <!-- ToC sidebar (sticky) -->
        <aside v-if="toc.length > 2" class="hidden lg:block">
          <div class="sticky top-24 rounded-xl border border-stone-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-journal-700 dark:text-primary-300">
              {{ t('static.table_of_contents') }}
            </p>
            <div class="space-y-0.5">
              <button
                v-for="item in toc"
                :key="item.id"
                class="block w-full rounded-md px-2 py-1.5 text-left text-xs leading-snug transition"
                :class="[
                  item.level === 3 ? 'pl-5' : '',
                  activeId === item.id
                    ? 'bg-primary-50 font-semibold text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                    : 'text-slate-500 hover:bg-stone-50 hover:text-journal-800 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-200'
                ]"
                @click="scrollTo(item.id)"
              >
                {{ item.text }}
              </button>
            </div>
          </div>
        </aside>
      </div>

      <!-- Empty content -->
      <div v-if="!content.trim()" class="flex flex-col items-center py-16">
        <FileText :size="48" class="text-slate-200 dark:text-slate-700" />
        <p class="mt-4 text-slate-400">{{ t('static.no_content') }}</p>
      </div>
    </template>
  </div>
</template>
