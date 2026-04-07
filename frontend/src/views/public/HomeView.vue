<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ArrowRight, FileText, Target, BarChart3, Send, ClipboardList, ShieldCheck, Unlock, DollarSign, Download } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import type { PaginatedResponse, Article } from '@/types/article'
import type { Volume } from '@/types/volume'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()
const localeStore = useLocaleStore()

useSeoMeta({
  title: 'Science and Innovation Journal',
  description: 'International scientific journal covering science, technology and innovation. Open access, peer-reviewed.',
})

interface HomeSettingsData {
  hero_title: Record<string, string>
  hero_subtitle: Record<string, string>
  about_title: Record<string, string>
  about_text: Record<string, string>
  cta_title: Record<string, string>
  cta_subtitle: Record<string, string>
  announcement_uz: string | null
  announcement_ru: string | null
  announcement_en: string | null
  announcement_active: boolean
}

const lang = computed(() => localeStore.current)
const hs = ref<HomeSettingsData | null>(null)
const latestArticles = ref<Article[]>([])
const currentVolume = ref<Volume | null>(null)
const stats = ref({ total_articles: 0, total_authors: 0, total_downloads: 0, total_volumes: 0 })
const loading = ref(true)
const activeTab = ref<'details' | 'authors' | 'policy'>('details')

const heroTitle = computed(() => hs.value?.hero_title?.[lang.value] || hs.value?.hero_title?.uz || t('home.hero_title'))
const heroSubtitle = computed(() => hs.value?.hero_subtitle?.[lang.value] || hs.value?.hero_subtitle?.uz || t('home.hero_subtitle'))
const aboutTitle = computed(() => hs.value?.about_title?.[lang.value] || hs.value?.about_title?.uz || t('nav.about_journal'))
const aboutText = computed(() => hs.value?.about_text?.[lang.value] || hs.value?.about_text?.uz || '')
const ctaTitle = computed(() => hs.value?.cta_title?.[lang.value] || hs.value?.cta_title?.uz || t('home.submit_cta_title'))
const ctaSubtitle = computed(() => hs.value?.cta_subtitle?.[lang.value] || hs.value?.cta_subtitle?.uz || t('home.submit_cta_desc'))

const articleTitle = (a: Article) => {
  const map = a.title as Record<string, string>
  return map?.[lang.value] || map?.uz || map?.en || 'Untitled'
}
const articleAuthors = (a: Article) => {
  const main = a.author?.full_name || ''
  const co = (a.co_authors || []).map(c => c.guest_name || c.user?.full_name).filter(Boolean)
  return [main, ...co].join(', ')
}

onMounted(async () => {
  try {
    const [articlesData, volumesData, homeSettings, statsData] = await Promise.all([
      api.get<PaginatedResponse<Article>>('/api/articles?limit=6&status=published'),
      api.get<Volume[]>('/api/volumes'),
      api.get<HomeSettingsData>('/api/home-settings').catch(() => null),
      api.get<typeof stats.value>('/api/stats/overview').catch(() => null),
    ])
    latestArticles.value = articlesData.items
    currentVolume.value = volumesData.find((v) => v.is_current) ?? volumesData[0] ?? null
    hs.value = homeSettings
    if (statsData) stats.value = statsData
  } catch { /* ignore */ }
  finally { loading.value = false }
})

const statItems = computed(() => [
  { value: stats.value.total_articles, label: t('home.stats_articles') },
  { value: stats.value.total_authors, label: t('home.stats_authors') },
  { value: stats.value.total_downloads, label: t('home.stats_downloads') },
  { value: stats.value.total_volumes, label: t('home.stats_volumes') },
])
</script>

<template>
  <div class="space-y-6">
    <!-- Banner Hero -->
    <section class="relative overflow-hidden rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 via-journal-700 to-journal-900 shadow-lg">
      <div class="absolute inset-0 opacity-[0.06]" style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 28px 28px;" />
      <div class="absolute -right-10 top-0 h-full w-2/3">
        <svg viewBox="0 0 400 300" class="h-full w-full opacity-20">
          <defs>
            <radialGradient id="g1" cx="50%" cy="50%">
              <stop offset="0%" stop-color="#eec96b" stop-opacity="0.4" />
              <stop offset="100%" stop-color="#eec96b" stop-opacity="0" />
            </radialGradient>
          </defs>
          <g stroke="#eec96b" stroke-width="1" fill="none" opacity="0.4">
            <path d="M 200 50 A 100 100 0 0 1 300 150" />
            <path d="M 200 70 A 80 80 0 0 1 280 150" />
            <path d="M 200 90 A 60 60 0 0 1 260 150" />
            <path d="M 150 150 Q 200 100 250 150 T 350 150" />
          </g>
          <circle cx="300" cy="150" r="80" fill="url(#g1)" />
        </svg>
      </div>
      <div class="relative p-8 sm:p-10 lg:p-12">
        <div class="max-w-2xl">
          <span class="inline-block rounded-full border border-primary-400/40 bg-primary-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-primary-300">
            {{ t('home.hero_badge') }}
          </span>
          <h1 class="mt-4 font-serif text-3xl font-bold text-primary-200 sm:text-4xl">
            {{ heroTitle }}
          </h1>
          <p class="mt-3 text-sm leading-relaxed text-slate-300 sm:text-base">{{ heroSubtitle }}</p>
        </div>

        <!-- Stats bar -->
        <div class="relative mt-8 grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm sm:grid-cols-4">
          <div
            v-for="stat in statItems"
            :key="stat.label"
            class="bg-journal-800/40 p-4 text-center"
          >
            <div class="font-serif text-2xl font-bold text-primary-200">{{ stat.value.toLocaleString() }}</div>
            <div class="mt-1 text-[11px] uppercase tracking-wider text-slate-400">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- About Section -->
    <section class="rounded-2xl border border-stone-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-800 sm:p-8">
      <h2 class="font-serif text-2xl font-bold text-journal-800 dark:text-primary-300">{{ aboutTitle }}</h2>
      <p class="mt-4 leading-relaxed text-slate-700 dark:text-slate-300">{{ aboutText || t('home.hero_subtitle') }}</p>
    </section>

    <!-- Apply Now Card -->
    <section class="rounded-2xl border-2 border-dashed border-primary-400 bg-stone-100 p-8 text-center dark:border-primary-600 dark:bg-journal-900">
      <p class="font-serif text-lg font-semibold text-journal-800 dark:text-primary-200">
        {{ ctaTitle }}
      </p>
      <p class="mt-2 text-sm text-slate-600 dark:text-slate-400">{{ ctaSubtitle }}</p>
      <RouterLink
        to="/author/submit"
        class="mt-5 inline-flex items-center gap-2 rounded-lg border-2 border-primary-600 bg-primary-500 px-6 py-2.5 text-sm font-bold text-journal-900 shadow-sm transition hover:bg-primary-400"
      >
        <Send :size="16" />
        {{ t('home.apply_now') }}
      </RouterLink>
    </section>

    <!-- Tabs -->
    <section class="rounded-2xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <!-- Tab nav -->
      <div class="flex border-b border-stone-200 dark:border-slate-700">
        <button
          v-for="tab in [
            { id: 'details', label: t('home.tab_details') },
            { id: 'authors', label: t('home.tab_authors') },
            { id: 'policy', label: t('home.tab_policy') },
          ]"
          :key="tab.id"
          class="flex-1 px-4 py-3 text-sm font-semibold transition"
          :class="activeTab === tab.id
            ? 'bg-stone-100 text-journal-800 border-b-2 border-primary-500 dark:bg-journal-900 dark:text-primary-300'
            : 'text-slate-500 hover:text-journal-700 dark:text-slate-400'"
          @click="activeTab = tab.id as any"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab content: 3 circular cards -->
      <div class="p-8">
        <div v-if="activeTab === 'details'" class="grid grid-cols-3 gap-6">
          <RouterLink to="/pages/about" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <FileText :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_details') }}</h3>
          </RouterLink>
          <RouterLink to="/pages/aims" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <Target :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_scope') }}</h3>
          </RouterLink>
          <RouterLink to="/pages/indexing" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <BarChart3 :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_metrics') }}</h3>
          </RouterLink>
        </div>

        <div v-else-if="activeTab === 'authors'" class="grid grid-cols-3 gap-6">
          <RouterLink to="/author/submit" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <Send :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_submissions') }}</h3>
          </RouterLink>
          <RouterLink to="/pages/author-guidelines" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <ClipboardList :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_guidelines') }}</h3>
          </RouterLink>
          <RouterLink to="/pages/review-process" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <ShieldCheck :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_peer_review') }}</h3>
          </RouterLink>
        </div>

        <div v-else class="grid grid-cols-2 gap-6 max-w-md mx-auto">
          <RouterLink to="/pages/open-access" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <Unlock :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_open_access') }}</h3>
          </RouterLink>
          <RouterLink to="/pages/plagiarism" class="group flex flex-col items-center gap-3">
            <div class="flex h-24 w-24 items-center justify-center rounded-full border-4 border-primary-300 bg-stone-100 shadow-md transition group-hover:border-primary-500 group-hover:shadow-lg dark:bg-journal-800">
              <ShieldCheck :size="32" class="text-primary-600 dark:text-primary-400" />
            </div>
            <h3 class="font-serif text-base font-bold text-journal-800 dark:text-primary-300">{{ t('home.card_plagiarism') }}</h3>
          </RouterLink>
        </div>
      </div>
    </section>

    <!-- Articles list -->
    <section>
      <h2 class="mb-4 border-b-2 border-primary-400 pb-2 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
        {{ t('home.latest_articles') }}
      </h2>

      <div v-if="loading" class="space-y-4">
        <div v-for="i in 3" :key="i" class="h-32 animate-pulse rounded-xl bg-stone-100 dark:bg-slate-800" />
      </div>

      <div v-else-if="!latestArticles.length" class="rounded-xl border border-stone-200 bg-white p-8 text-center text-slate-400 dark:border-slate-700 dark:bg-slate-800">
        {{ t('articles.no_results') }}
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="article in latestArticles"
          :key="article.id"
          class="group rounded-xl border border-stone-200 bg-white p-5 transition hover:border-primary-400 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
        >
          <RouterLink :to="`/articles/${article.id}`" class="block">
            <h3 class="font-serif text-base font-bold text-journal-800 transition group-hover:text-primary-700 dark:text-slate-200 dark:group-hover:text-primary-400">
              {{ articleTitle(article) }}
            </h3>
            <p class="mt-1 text-sm text-slate-600 dark:text-slate-400">
              {{ articleAuthors(article) }}
            </p>
          </RouterLink>
          <div v-if="article.doi" class="mt-3 flex items-center gap-2 text-xs text-primary-700 dark:text-primary-400">
            <span class="h-4 w-4 rounded-full bg-primary-500 flex-shrink-0" />
            <a :href="`https://doi.org/${article.doi}`" target="_blank" rel="noopener" class="hover:underline font-mono">
              https://doi.org/{{ article.doi }}
            </a>
          </div>
          <div class="mt-3 flex items-center gap-2">
            <RouterLink
              v-if="article.pdf_file_path"
              :to="`/articles/${article.id}`"
              class="inline-flex items-center gap-1.5 rounded-md bg-primary-100 px-3 py-1.5 text-xs font-semibold text-primary-800 transition hover:bg-primary-200 dark:bg-primary-950 dark:text-primary-300"
            >
              <FileText :size="12" />
              Full text (PDF)
            </RouterLink>
            <span v-if="article.published_date" class="ml-auto text-xs text-slate-400">
              {{ new Date(article.published_date).getFullYear() }}
            </span>
          </div>
        </div>
      </div>

      <div class="mt-6 text-center">
        <RouterLink
          to="/articles"
          class="inline-flex items-center gap-2 text-sm font-semibold text-primary-700 hover:text-primary-800 dark:text-primary-400"
        >
          {{ t('common.view_all') }}
          <ArrowRight :size="15" />
        </RouterLink>
      </div>
    </section>
  </div>
</template>
