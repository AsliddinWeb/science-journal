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
  license_type?: string | null

  footer_description?: Record<string, string>
  contact_email?: string | null
  contact_phone?: string | null
  contact_address?: string | null
  social_telegram?: string | null
  social_facebook?: string | null
  social_instagram?: string | null
  social_youtube?: string | null
  social_linkedin?: string | null
  social_twitter?: string | null

  // Legacy fallback
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
 * Single source of truth for site branding, footer content and contact info.
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
    || pick(data.value?.hero_title, DEFAULT_NAME)
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
  const licenseType = computed(() => data.value?.license_type || '')

  const footerDescription = computed(() => pick(data.value?.footer_description, { uz: '', ru: '', en: '' }))

  const contactEmail = computed(() => data.value?.contact_email || '')
  const contactPhone = computed(() => data.value?.contact_phone || '')
  const contactAddress = computed(() => data.value?.contact_address || '')

  const socials = computed(() => {
    const d = data.value
    if (!d) return [] as { label: string; url: string }[]
    const items: { label: string; url: string }[] = []
    if (d.social_telegram)  items.push({ label: 'Telegram',  url: d.social_telegram })
    if (d.social_facebook)  items.push({ label: 'Facebook',  url: d.social_facebook })
    if (d.social_instagram) items.push({ label: 'Instagram', url: d.social_instagram })
    if (d.social_youtube)   items.push({ label: 'YouTube',   url: d.social_youtube })
    if (d.social_linkedin)  items.push({ label: 'LinkedIn',  url: d.social_linkedin })
    if (d.social_twitter)   items.push({ label: 'X / Twitter', url: d.social_twitter })
    return items
  })

  return {
    data,
    loaded,
    load,
    siteName,
    tagline,
    logoUrl,
    issn,
    licenseType,
    footerDescription,
    contactEmail,
    contactPhone,
    contactAddress,
    socials,
  }
})
