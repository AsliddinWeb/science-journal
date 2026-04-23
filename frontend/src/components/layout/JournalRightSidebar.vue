<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { BookOpen, ArrowRight } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { useSiteInfoStore } from '@/stores/siteInfo'

const { t } = useI18n()
const siteInfo = useSiteInfoStore()

interface HomeSettings {
  hero_title: Record<string, string>
  about_image_url: string | null
  issn_online: string | null
  issn_print: string | null
  license_type: string | null
}

interface IndexingItem { id: string; name: string; url: string; logo_url?: string }

const localeStore = useLocaleStore()
const hs = ref<HomeSettings | null>(null)
const indexing = ref<IndexingItem[]>([])

const lang = computed(() => localeStore.current)
const journalTitle = computed(() => siteInfo.siteName)
const coverImage = computed(() => {
  if (!hs.value?.about_image_url) return null
  return hs.value.about_image_url.startsWith('/') ? hs.value.about_image_url : `/api/uploads/${hs.value.about_image_url}`
})

onMounted(async () => {
  try {
    const [settings, idx] = await Promise.all([
      api.get<HomeSettings>('/api/home-settings').catch(() => null),
      api.get<IndexingItem[]>('/api/indexing').catch(() => []),
    ])
    hs.value = settings
    indexing.value = idx ?? []
  } catch { /* ignore */ }
})

function resolveLogo(url?: string) {
  if (!url) return null
  return url.startsWith('http') || url.startsWith('/') ? url : `/api/uploads/${url}`
}
</script>

<template>
  <aside class="w-full space-y-6">
    <!-- Journal Cover Card -->
    <div class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <!-- Cover image -->
      <div class="aspect-[3/4] bg-gradient-to-br from-primary-600 to-primary-800">
        <div v-if="!siteInfo.loaded" class="skeleton h-full w-full rounded-none" />
        <img
          v-else-if="coverImage"
          :src="coverImage"
          :alt="journalTitle"
          class="h-full w-full object-cover"
        />
        <div v-else class="flex h-full w-full flex-col items-center justify-center p-6 text-center">
          <BookOpen :size="48" class="mb-4 text-white/30" />
          <span class="font-serif text-xl font-bold text-white/90">{{ journalTitle }}</span>
        </div>
      </div>
      <!-- Info -->
      <div class="bg-journal-800 p-5 text-xs text-slate-300">
        <div v-if="hs?.issn_online" class="mb-1">
          <span class="font-semibold text-primary-300">Online ISSN:</span> {{ hs.issn_online }}
        </div>
        <div v-if="hs?.issn_print" class="mb-1">
          <span class="font-semibold text-primary-300">Print ISSN:</span> {{ hs.issn_print }}
        </div>
        <div v-if="hs?.license_type" class="mb-1">
          <span class="font-semibold text-primary-300">License:</span> {{ hs.license_type }}
        </div>
        <RouterLink
          to="/pages/about"
          class="mt-3 inline-flex items-center gap-1 text-[11px] font-semibold text-primary-300 hover:text-primary-200"
        >
          MORE
          <ArrowRight :size="12" />
        </RouterLink>
      </div>
    </div>

    <!-- Indexing and Abstracting -->
    <div v-if="indexing.length" class="overflow-hidden rounded-2xl border border-stone-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div class="bg-journal-900 px-5 py-3 text-center">
        <h3 class="font-serif text-sm font-bold uppercase tracking-wider text-primary-300">
          {{ t('sidebar.indexing_abstracting') }}
        </h3>
      </div>
      <div class="space-y-3 p-4">
        <a
          v-for="db in indexing"
          :key="db.id"
          :href="db.url"
          target="_blank"
          rel="noopener noreferrer"
          class="block overflow-hidden rounded-lg border border-stone-200 transition hover:border-primary-400 hover:shadow-md dark:border-slate-600"
          :title="db.name"
        >
          <img
            v-if="db.logo_url"
            :src="resolveLogo(db.logo_url)!"
            :alt="db.name"
            class="h-20 w-full object-contain bg-white p-2"
          />
          <div v-else class="flex h-20 items-center justify-center bg-stone-50 px-3 text-center text-xs font-semibold text-slate-700 dark:bg-slate-700 dark:text-slate-200">
            {{ db.name }}
          </div>
        </a>
      </div>
    </div>
  </aside>
</template>
