import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'

export interface SiteInfoData {
  site_name?: Record<string, string>
  site_tagline?: Record<string, string>
  site_logo_url?: string | null
  issn_online?: string | null
  issn_print?: string | null
  // Legacy fallback — some places still use hero_title as the display name
  hero_title?: Record<string, string>
}

const DEFAULT_NAME = {
  uz: 'Filologiya va Ijtimoiy fanlar',
  ru: 'Филология и Социальные науки',
  en: 'Philology and Social Sciences',
}

const DEFAULT_TAGLINE = {
  uz: 'Academicbook',
  ru: 'Academicbook',
  en: 'Academicbook',
}

/**
 * Single source of truth for site branding (name, logo, tagline).
 * Loaded once from /api/home-settings; all components read from here.
 */
export const useSiteInfoStore = defineStore('siteInfo', () => {
  const locale = useLocaleStore()
  const data = ref<SiteInfoData | null>(null)
  const loaded = ref(false)

  async function load(force = false) {
    if (loaded.value && !force) return
    try {
      data.value = await api.get<SiteInfoData>('/api/home-settings')
    } catch {
      data.value = null
    } finally {
      loaded.value = true
    }
  }

  function pick(dict: Record<string, string> | undefined, fallback: Record<string, string>): string {
    const l = locale.current
    return dict?.[l] || dict?.en || dict?.uz || dict?.ru || fallback[l as keyof typeof fallback] || fallback.en
  }

  const siteName = computed(() =>
    pick(data.value?.site_name, DEFAULT_NAME)
    || pick(data.value?.hero_title, DEFAULT_NAME)  // graceful fallback
    || DEFAULT_NAME.en
  )

  const tagline = computed(() => pick(data.value?.site_tagline, DEFAULT_TAGLINE))

  const logoUrl = computed(() => {
    const u = data.value?.site_logo_url
    if (!u) return ''
    if (u.startsWith('http') || u.startsWith('/')) return u
    return `/api/uploads/${u}`
  })

  const issn = computed(() => data.value?.issn_online || data.value?.issn_print || '')

  return { data, loaded, load, siteName, tagline, logoUrl, issn }
})
