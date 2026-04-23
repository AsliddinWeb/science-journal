<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  BookOpen, ExternalLink, Mail, Phone, MapPin,
  Send, Facebook, Instagram, Youtube, Linkedin, Twitter,
} from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import { api } from '@/composables/useApi'
import { useSiteInfoStore } from '@/stores/siteInfo'

const { t } = useI18n()
const siteInfo = useSiteInfoStore()
const currentYear = new Date().getFullYear()

// Map social labels to icon components
const socialIcons: Record<string, any> = {
  'Telegram': Send,
  'Facebook': Facebook,
  'Instagram': Instagram,
  'YouTube': Youtube,
  'LinkedIn': Linkedin,
  'X / Twitter': Twitter,
}

// Indexing databases (managed at /admin/indexing)
interface IndexingItem { id: string; name: string; url: string; logo_url?: string }
const indexing = ref<IndexingItem[]>([])

onMounted(async () => {
  try {
    indexing.value = await api.get<IndexingItem[]>('/api/indexing')
  } catch { /* silent */ }
})

function resolveLogo(u?: string) {
  if (!u) return ''
  return u.startsWith('http') || u.startsWith('/') ? u : `/api/uploads/${u}`
}
</script>

<template>
  <footer class="border-t border-journal-700 bg-journal-900 text-slate-300">

    <!-- Indexing row — real data from /api/indexing -->
    <div v-if="indexing.length" class="border-b border-journal-800 bg-journal-950">
      <div class="mx-auto max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
        <p class="mb-4 text-center text-xs font-semibold uppercase tracking-wider text-slate-400">
          {{ t('footer.indexed_in') }}
        </p>
        <div class="flex flex-wrap items-center justify-center gap-3">
          <a
            v-for="db in indexing"
            :key="db.id"
            :href="db.url"
            target="_blank"
            rel="noopener noreferrer"
            class="flex items-center gap-2 rounded-lg border border-slate-700 bg-journal-800 px-3 py-2 text-xs font-medium text-slate-300 transition hover:border-primary-400 hover:text-primary-200"
          >
            <img
              v-if="db.logo_url"
              :src="resolveLogo(db.logo_url)"
              :alt="db.name"
              class="h-5 w-auto max-w-[24px] object-contain"
            />
            {{ db.name }}
          </a>
        </div>
      </div>
    </div>

    <!-- Main footer -->
    <div class="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div class="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Brand -->
        <div class="sm:col-span-2 lg:col-span-1">
          <RouterLink to="/" class="flex items-center gap-2.5">
            <template v-if="!siteInfo.loaded">
              <div class="skeleton h-9 w-9 rounded-xl" />
              <div class="skeleton h-5 w-32 rounded" />
            </template>
            <template v-else>
              <img
                v-if="siteInfo.logoUrl"
                :src="siteInfo.logoUrl"
                :alt="siteInfo.siteName"
                class="h-9 w-auto max-w-[100px] object-contain"
              />
              <div v-else class="flex h-9 w-9 items-center justify-center rounded-xl bg-primary-500">
                <BookOpen :size="18" class="text-white" />
              </div>
              <span class="font-serif text-lg font-semibold text-primary-200">
                {{ siteInfo.siteName }}
              </span>
            </template>
          </RouterLink>

          <p v-if="siteInfo.footerDescription" class="mt-4 text-sm leading-relaxed text-slate-400">
            {{ siteInfo.footerDescription }}
          </p>

          <p v-if="siteInfo.issn" class="mt-2 text-xs text-slate-500">
            ISSN: {{ siteInfo.issn }}
          </p>

          <div v-if="siteInfo.licenseType" class="mt-4 inline-flex items-center gap-1.5 rounded-lg bg-journal-800 px-3 py-2">
            <svg viewBox="0 0 100 100" class="h-5 w-5 shrink-0" aria-hidden="true">
              <circle cx="50" cy="50" r="48" fill="#a6ce39"/>
              <path d="M 22 50 L 45 50 L 45 22" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/>
              <path d="M 78 50 L 55 50 L 55 78" stroke="white" stroke-width="10" fill="none" stroke-linecap="round"/>
            </svg>
            <span class="text-xs font-medium text-slate-300">{{ siteInfo.licenseType }}</span>
          </div>
        </div>

        <!-- Quick Links -->
        <div>
          <h3 class="text-sm font-semibold uppercase tracking-wider text-primary-300">
            {{ t('footer.quick_links') }}
          </h3>
          <ul class="mt-4 flex flex-col gap-2.5">
            <li v-for="link in [
              { to: '/articles', label: t('nav.articles') },
              { to: '/archive', label: t('nav.archive') },
              { to: '/editorial-board', label: t('nav.editorial') },
              { to: '/pages/indexing', label: t('nav.indexing') },
              { to: '/contact', label: t('nav.contact') },
            ]" :key="link.to">
              <RouterLink :to="link.to" class="text-sm text-slate-400 transition-colors hover:text-primary-300">
                {{ link.label }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- For Authors -->
        <div>
          <h3 class="text-sm font-semibold uppercase tracking-wider text-primary-300">
            {{ t('footer.for_authors') }}
          </h3>
          <ul class="mt-4 flex flex-col gap-2.5">
            <li v-for="link in [
              { to: '/pages/author-guidelines', label: t('footer.author_guidelines') },
              { to: '/pages/review-process', label: t('footer.review_process') },
              { to: '/pages/open-access', label: t('footer.open_access') },
              { to: '/pages/plagiarism', label: t('footer.plagiarism_policy') },
            ]" :key="link.to">
              <RouterLink :to="link.to" class="text-sm text-slate-400 transition-colors hover:text-primary-300">
                {{ link.label }}
              </RouterLink>
            </li>
          </ul>
        </div>

        <!-- Contact -->
        <div>
          <h3 class="text-sm font-semibold uppercase tracking-wider text-primary-300">
            {{ t('footer.contact_us') }}
          </h3>
          <ul class="mt-4 flex flex-col gap-3 text-sm text-slate-400">
            <li v-if="siteInfo.contactEmail" class="flex items-start gap-2">
              <Mail :size="14" class="mt-0.5 text-slate-500" />
              <a :href="`mailto:${siteInfo.contactEmail}`" class="transition-colors hover:text-primary-300">
                {{ siteInfo.contactEmail }}
              </a>
            </li>
            <li v-if="siteInfo.contactPhone" class="flex items-start gap-2">
              <Phone :size="14" class="mt-0.5 text-slate-500" />
              <a :href="`tel:${siteInfo.contactPhone.replace(/\s+/g, '')}`" class="transition-colors hover:text-primary-300">
                {{ siteInfo.contactPhone }}
              </a>
            </li>
            <li v-if="siteInfo.contactAddress" class="flex items-start gap-2">
              <MapPin :size="14" class="mt-0.5 text-slate-500" />
              <span>{{ siteInfo.contactAddress }}</span>
            </li>
          </ul>

          <!-- Social icons -->
          <div v-if="siteInfo.socials.length" class="mt-5 flex flex-wrap items-center gap-2">
            <a
              v-for="s in siteInfo.socials"
              :key="s.label"
              :href="s.url"
              target="_blank"
              rel="noopener noreferrer"
              :title="s.label"
              class="flex h-8 w-8 items-center justify-center rounded-lg border border-journal-700 bg-journal-800 text-slate-400 transition hover:border-primary-400 hover:text-primary-300"
            >
              <component :is="socialIcons[s.label] || ExternalLink" :size="14" />
            </a>
          </div>
        </div>
      </div>

      <!-- Bottom bar -->
      <div class="mt-10 flex flex-col items-center justify-between gap-4 border-t border-journal-800 pt-8 sm:flex-row">
        <p class="text-sm text-slate-500">
          &copy; {{ currentYear }} {{ siteInfo.siteName }}. {{ t('footer.rights') }}
        </p>
        <div class="flex items-center gap-4 text-xs text-slate-500">
          <RouterLink to="/pages/privacy" class="transition-colors hover:text-primary-300">Privacy</RouterLink>
          <RouterLink to="/pages/terms" class="transition-colors hover:text-primary-300">Terms</RouterLink>
          <RouterLink to="/pages/license-agreement" class="transition-colors hover:text-primary-300">License</RouterLink>
        </div>
      </div>
    </div>
  </footer>
</template>
