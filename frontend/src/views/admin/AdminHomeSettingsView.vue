<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Loader2, Image, X, Palette, Film, Upload, Mail, Phone, MapPin, Share2 } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import { THEMES, DEFAULT_THEME_ID } from '@/theme/themes'
import { useSiteThemeStore } from '@/stores/siteTheme'
import { useSiteInfoStore } from '@/stores/siteInfo'

const { t } = useI18n()
const toast = useToast()

const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const siteTheme = useSiteThemeStore()
const siteInfo = useSiteInfoStore()

const uploadingVideo = ref(false)
const uploadingPoster = ref(false)
const uploadingLogo = ref(false)

const form = ref({
  site_logo_url: '',
  site_name: { uz: '', ru: '', en: '' },
  site_tagline: { uz: '', ru: '', en: '' },
  footer_description: { uz: '', ru: '', en: '' },
  contact_email: '',
  contact_phone: '',
  contact_address: '',
  social_telegram: '',
  social_facebook: '',
  social_instagram: '',
  social_youtube: '',
  social_linkedin: '',
  social_twitter: '',
  hero_title: { uz: '', ru: '', en: '' },
  hero_subtitle: { uz: '', ru: '', en: '' },
  hero_issn: '',
  hero_video_url: '',
  hero_video_poster_url: '',
  hero_video_active: false,
  about_title: { uz: '', ru: '', en: '' },
  about_text: { uz: '', ru: '', en: '' },
  about_image_url: '',
  issn_online: '',
  issn_print: '',
  license_type: '',
  announcement_uz: '',
  announcement_ru: '',
  announcement_en: '',
  announcement_active: false,
  cta_title: { uz: '', ru: '', en: '' },
  cta_subtitle: { uz: '', ru: '', en: '' },
  theme: DEFAULT_THEME_ID,
})

function pickTheme(id: string) {
  form.value.theme = id
  // Live preview — also apply to current page
  siteTheme.set(id)
}

function swatchStyle(rgb: string): Record<string, string> {
  return { backgroundColor: `rgb(${rgb})` }
}

onMounted(async () => {
  try {
    const data = await api.get<any>('/api/home-settings')
    form.value = {
      site_logo_url: data.site_logo_url || '',
      site_name: data.site_name || { uz: '', ru: '', en: '' },
      site_tagline: data.site_tagline || { uz: '', ru: '', en: '' },
      footer_description: data.footer_description || { uz: '', ru: '', en: '' },
      contact_email: data.contact_email || '',
      contact_phone: data.contact_phone || '',
      contact_address: data.contact_address || '',
      social_telegram: data.social_telegram || '',
      social_facebook: data.social_facebook || '',
      social_instagram: data.social_instagram || '',
      social_youtube: data.social_youtube || '',
      social_linkedin: data.social_linkedin || '',
      social_twitter: data.social_twitter || '',
      hero_title: data.hero_title || { uz: '', ru: '', en: '' },
      hero_subtitle: data.hero_subtitle || { uz: '', ru: '', en: '' },
      hero_issn: data.hero_issn || '',
      hero_video_url: data.hero_video_url || '',
      hero_video_poster_url: data.hero_video_poster_url || '',
      hero_video_active: !!data.hero_video_active,
      about_title: data.about_title || { uz: '', ru: '', en: '' },
      about_text: data.about_text || { uz: '', ru: '', en: '' },
      about_image_url: data.about_image_url || '',
      issn_online: data.issn_online || '',
      issn_print: data.issn_print || '',
      license_type: data.license_type || '',
      announcement_uz: data.announcement_uz || '',
      announcement_ru: data.announcement_ru || '',
      announcement_en: data.announcement_en || '',
      announcement_active: data.announcement_active || false,
      cta_title: data.cta_title || { uz: '', ru: '', en: '' },
      cta_subtitle: data.cta_subtitle || { uz: '', ru: '', en: '' },
      theme: (THEMES.find(t => t.id === data.theme)?.id) || DEFAULT_THEME_ID,
    }
  } catch {}
  finally { loading.value = false }
})

async function save() {
  saving.value = true
  try {
    await api.put('/api/home-settings', {
      ...form.value,
      about_image_url: form.value.about_image_url || null,
      site_logo_url: form.value.site_logo_url || null,
    })
    // Once saved, make the chosen theme the site-wide default — clear any
    // previous localStorage override so other clients pick up the new default.
    try { localStorage.removeItem('site-theme') } catch { /* ignore */ }
    siteTheme.set(form.value.theme)
    // Refresh site branding so navbar/footer update immediately
    await siteInfo.load(true)
    toast.success('Saqlandi')
  } catch { toast.error('Xatolik') }
  finally { saving.value = false }
}

async function uploadImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.about_image_url = res.s3_key
  } catch { toast.error('Rasm yuklanmadi') }
  finally { uploading.value = false }
}

async function uploadHeroVideo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingVideo.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/video', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.hero_video_url = res.s3_key
    form.value.hero_video_active = true
    toast.success('Video yuklandi')
  } catch (err: any) {
    const msg = err?.response?.data?.detail
    toast.error(typeof msg === 'string' ? msg : 'Video yuklanmadi')
  } finally {
    uploadingVideo.value = false
  }
}

async function uploadLogo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingLogo.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.site_logo_url = res.s3_key
    toast.success('Logo yuklandi')
  } catch { toast.error('Logo yuklanmadi') }
  finally { uploadingLogo.value = false }
}

async function uploadHeroPoster(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingPoster.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.hero_video_poster_url = res.s3_key
  } catch { toast.error('Poster yuklanmadi') }
  finally { uploadingPoster.value = false }
}
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.homeSettings.title') }}</h1>
      <AppButton :loading="saving" @click="save"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24"><AppSpinner :size="36" class="text-primary-500" /></div>

    <div v-else class="space-y-6">
      <!-- ══ Branding (logo + jurnal nomi) ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-1 flex items-center gap-2">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">Logo va jurnal nomi</h2>
        </div>
        <p class="mb-4 text-xs text-slate-500 dark:text-slate-400">
          Logo va jurnal nomi saytning hamma joyida (navbar, footer, SEO, iqtiboslar) shu yerdan olinadi.
        </p>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-[220px_1fr]">
          <!-- Logo upload -->
          <div>
            <label class="label-base">Logo (yuqorida ko'rinadi)</label>
            <div class="flex flex-col items-start gap-3 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-4 dark:border-slate-600 dark:bg-slate-800/40">
              <div class="flex h-20 w-full items-center justify-center overflow-hidden rounded-lg bg-white dark:bg-slate-900">
                <img
                  v-if="form.site_logo_url"
                  :src="form.site_logo_url.startsWith('http') || form.site_logo_url.startsWith('/') ? form.site_logo_url : `/api/uploads/${form.site_logo_url}`"
                  class="max-h-16 w-auto object-contain"
                />
                <span v-else class="text-xs text-slate-400">Logo yo'q</span>
              </div>
              <div class="flex w-full items-center gap-2">
                <label class="flex flex-1 cursor-pointer items-center gap-2 rounded-lg bg-primary-600 px-3 py-2 text-xs font-medium text-white hover:bg-primary-700">
                  <Loader2 v-if="uploadingLogo" :size="14" class="animate-spin" />
                  <Image v-else :size="14" />
                  {{ uploadingLogo ? 'Yuklanmoqda...' : 'Logo yuklash' }}
                  <input type="file" accept="image/*" class="hidden" @change="uploadLogo" />
                </label>
                <button
                  v-if="form.site_logo_url"
                  type="button"
                  class="rounded-lg border border-slate-200 p-2 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:border-slate-600"
                  :title="t('common.delete')"
                  @click="form.site_logo_url = ''"
                >
                  <X :size="14" />
                </button>
              </div>
            </div>
          </div>

          <!-- Name + tagline -->
          <div class="space-y-4">
            <div>
              <label class="label-base">Jurnal nomi ({{ langTab.toUpperCase() }})</label>
              <input
                v-model="form.site_name[langTab]"
                class="input-base w-full font-serif text-lg"
                placeholder="masalan: Filologiya va Ijtimoiy fanlar"
              />
            </div>
            <div>
              <label class="label-base">Tagline — logo tepasida ko'rinadi ({{ langTab.toUpperCase() }})</label>
              <input
                v-model="form.site_tagline[langTab]"
                class="input-base w-full"
                placeholder="masalan: Ilmiy jurnal"
              />
              <p class="mt-1 text-[11px] text-slate-400">Navbar'da jurnal nomidan yuqorida kichik matn sifatida chiqadi (Academicbook ornida).</p>
            </div>
          </div>
        </div>
      </section>

      <!-- ══ Theme picker ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center gap-2">
          <Palette :size="18" class="text-primary-600 dark:text-primary-400" />
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">Sayt rang mavzusi</h2>
          <span class="ml-auto text-xs text-slate-400">Tanlangan: <strong class="text-slate-700 dark:text-slate-200">{{ form.theme }}</strong></span>
        </div>
        <p class="mb-4 text-xs text-slate-500 dark:text-slate-400">
          Admin tanlagan mavzu barcha foydalanuvchilar uchun standart sifatida qo'llaniladi. Quyidagi variantlardan birini tanlang — chap paneldagi ranglar darhol yangilanadi.
        </p>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-5">
          <button
            v-for="theme in THEMES"
            :key="theme.id"
            type="button"
            class="group relative flex flex-col gap-2 rounded-xl border bg-white p-3 text-left transition hover:shadow-md dark:bg-slate-800"
            :class="form.theme === theme.id
              ? 'border-primary-500 ring-2 ring-primary-500/40'
              : 'border-slate-200 dark:border-slate-700 hover:border-primary-300'"
            @click="pickTheme(theme.id)"
          >
            <!-- Swatches -->
            <div class="flex h-8 overflow-hidden rounded-md">
              <span class="flex-1" :style="swatchStyle(theme.primary['300'])" />
              <span class="flex-1" :style="swatchStyle(theme.primary['500'])" />
              <span class="flex-1" :style="swatchStyle(theme.primary['700'])" />
              <span class="flex-1" :style="swatchStyle(theme.journal['800'])" />
            </div>
            <div>
              <p class="text-sm font-semibold text-slate-900 dark:text-slate-100">{{ theme.label }}</p>
              <p v-if="theme.description" class="mt-0.5 text-[11px] leading-snug text-slate-500 dark:text-slate-400">
                {{ theme.description }}
              </p>
            </div>
            <Check
              v-if="form.theme === theme.id"
              :size="16"
              class="absolute right-2 top-2 rounded-full bg-primary-500 p-0.5 text-white shadow"
            />
          </button>
        </div>
      </section>

      <!-- Lang tabs -->
      <div class="sticky top-16 z-10 flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="flex-1 rounded-md px-4 py-2 text-sm font-medium transition" :class="langTab === l ? 'bg-primary-600 text-white shadow' : 'text-slate-500 hover:text-slate-700'" @click="langTab = l">{{ l.toUpperCase() }}</button>
      </div>

      <!-- ══ Hero ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Hero</h2>
        <div class="space-y-4">
          <div>
            <label class="label-base">{{ t('admin.homeSettings.heroTitle') }} ({{ langTab.toUpperCase() }})</label>
            <input v-model="form.hero_title[langTab]" class="input-base w-full text-lg font-serif" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.homeSettings.heroSubtitle') }} ({{ langTab.toUpperCase() }})</label>
            <textarea v-model="form.hero_subtitle[langTab]" rows="3" class="input-base w-full resize-none" />
          </div>
          <div>
            <label class="label-base">ISSN badge</label>
            <input v-model="form.hero_issn" class="input-base w-64" placeholder="ISSN: 2181-0842" />
          </div>
        </div>
      </section>

      <!-- ══ Hero Video / Announcement ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center gap-2">
          <Film :size="18" class="text-primary-600 dark:text-primary-400" />
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">Hero video / E'lon</h2>
          <label class="ml-auto flex cursor-pointer items-center gap-2 text-sm">
            <input v-model="form.hero_video_active" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />
            <span class="text-slate-700 dark:text-slate-300">{{ t('common.active') }}</span>
          </label>
        </div>
        <p class="mb-4 text-xs text-slate-500 dark:text-slate-400">
          Bosh sahifa hero qismida ixtiyoriy video ko'rsating. YouTube/Vimeo havolasini yoki fayl yuklang (MP4/WebM, 200 MB gacha).
        </p>

        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <!-- URL + file upload -->
          <div class="space-y-2">
            <label class="label-base">Video URL yoki yuklangan fayl</label>
            <input
              v-model="form.hero_video_url"
              class="input-base w-full font-mono text-xs"
              placeholder="https://youtu.be/… yoki videos/uuid.mp4"
            />
            <div class="flex items-center gap-2">
              <label class="flex flex-1 cursor-pointer items-center gap-2 rounded-lg border-2 border-dashed border-slate-300 px-3 py-2 text-sm hover:border-primary-400 dark:border-slate-600">
                <Loader2 v-if="uploadingVideo" :size="16" class="animate-spin text-primary-500" />
                <Upload v-else :size="16" class="text-slate-400" />
                <span class="text-slate-500">{{ uploadingVideo ? 'Yuklanmoqda...' : 'Video yuklash (MP4/WebM)' }}</span>
                <input type="file" accept="video/mp4,video/webm,video/ogg,video/quicktime" class="hidden" @change="uploadHeroVideo" />
              </label>
              <button
                v-if="form.hero_video_url"
                class="rounded-lg border border-slate-200 p-2 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:border-slate-600 dark:hover:bg-red-900/30"
                type="button"
                :title="t('common.delete')"
                @click="form.hero_video_url = ''"
              >
                <X :size="14" />
              </button>
            </div>
          </div>

          <!-- Poster -->
          <div class="space-y-2">
            <label class="label-base">Video poster (ixtiyoriy — faqat MP4 uchun)</label>
            <div v-if="form.hero_video_poster_url" class="relative inline-block">
              <img
                :src="form.hero_video_poster_url.startsWith('http') || form.hero_video_poster_url.startsWith('/') ? form.hero_video_poster_url : `/api/uploads/${form.hero_video_poster_url}`"
                class="h-24 rounded-lg object-cover"
              />
              <button
                type="button"
                class="absolute -right-2 -top-2 rounded-full bg-red-500 p-1 text-white shadow hover:bg-red-600"
                @click="form.hero_video_poster_url = ''"
              >
                <X :size="12" />
              </button>
            </div>
            <label class="flex cursor-pointer items-center gap-2 rounded-lg border-2 border-dashed border-slate-300 px-3 py-2 text-sm hover:border-primary-400 dark:border-slate-600">
              <Loader2 v-if="uploadingPoster" :size="16" class="animate-spin text-primary-500" />
              <Image v-else :size="16" class="text-slate-400" />
              <span class="text-slate-500">{{ uploadingPoster ? 'Yuklanmoqda...' : 'Poster yuklash (JPEG/PNG)' }}</span>
              <input type="file" accept="image/*" class="hidden" @change="uploadHeroPoster" />
            </label>
          </div>
        </div>
      </section>

      <!-- ══ About ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.homeSettings.aboutSection') }}</h2>
        <div class="space-y-4">
          <div>
            <label class="label-base">{{ t('admin.homeSettings.aboutTitle') }} ({{ langTab.toUpperCase() }})</label>
            <input v-model="form.about_title[langTab]" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.homeSettings.aboutText') }} ({{ langTab.toUpperCase() }})</label>
            <textarea v-model="form.about_text[langTab]" rows="4" class="input-base w-full resize-none" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.homeSettings.aboutImage') }}</label>
            <div v-if="form.about_image_url" class="mb-2 relative inline-block">
              <img :src="`/api/uploads/${form.about_image_url}`" class="h-32 rounded-xl object-cover" />
              <button class="absolute -right-2 -top-2 rounded-full bg-red-500 p-1 text-white shadow hover:bg-red-600" @click="form.about_image_url = ''"><X :size="12" /></button>
            </div>
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border-2 border-dashed border-slate-300 px-4 py-3 hover:border-primary-400 dark:border-slate-600">
              <Loader2 v-if="uploading" :size="18" class="animate-spin text-primary-500" />
              <Image v-else :size="18" class="text-slate-400" />
              <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : 'Rasm yuklash (JPEG, PNG, WebP)' }}</span>
              <input type="file" accept="image/*" class="hidden" @change="uploadImage" />
            </label>
          </div>
          <div class="grid grid-cols-3 gap-4">
            <div>
              <label class="label-base">ISSN (Online)</label>
              <input v-model="form.issn_online" class="input-base w-full font-mono" placeholder="2181-0842" />
            </div>
            <div>
              <label class="label-base">ISSN (Print)</label>
              <input v-model="form.issn_print" class="input-base w-full font-mono" placeholder="" />
            </div>
            <div>
              <label class="label-base">{{ t('admin.homeSettings.license') }}</label>
              <input v-model="form.license_type" class="input-base w-full" placeholder="CC BY 4.0" />
            </div>
          </div>
        </div>
      </section>

      <!-- ══ Announcement ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.homeSettings.announcement') }}</h2>
          <label class="flex cursor-pointer items-center gap-2 text-sm">
            <input v-model="form.announcement_active" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />
            {{ t('common.active') }}
          </label>
        </div>
        <div class="space-y-3">
          <div>
            <label class="label-base">UZ</label>
            <input v-model="form.announcement_uz" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">RU</label>
            <input v-model="form.announcement_ru" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">EN</label>
            <input v-model="form.announcement_en" class="input-base w-full" />
          </div>
        </div>
      </section>

      <!-- ══ CTA ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.homeSettings.ctaSection') }}</h2>
        <div class="space-y-4">
          <div>
            <label class="label-base">{{ t('admin.homeSettings.ctaTitle') }} ({{ langTab.toUpperCase() }})</label>
            <input v-model="form.cta_title[langTab]" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.homeSettings.ctaSubtitle') }} ({{ langTab.toUpperCase() }})</label>
            <textarea v-model="form.cta_subtitle[langTab]" rows="2" class="input-base w-full resize-none" />
          </div>
        </div>
      </section>

      <!-- ══ Footer — tavsif, kontakt, ijtimoiy tarmoqlar ══ -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Footer — tavsif va kontakt</h2>

        <!-- Description per language -->
        <div class="mb-6">
          <label class="label-base">Footer tavsifi ({{ langTab.toUpperCase() }})</label>
          <textarea
            v-model="form.footer_description[langTab]"
            rows="3"
            class="input-base w-full resize-none"
            placeholder="Jurnal haqida qisqa ma'lumot — logo ostidagi matn"
          />
        </div>

        <!-- Contact -->
        <h3 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">Aloqa</h3>
        <div class="mb-6 grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label class="label-base flex items-center gap-1.5"><Mail :size="13" /> Email</label>
            <input v-model="form.contact_email" type="email" class="input-base w-full" placeholder="editor@academicbook.uz" />
          </div>
          <div>
            <label class="label-base flex items-center gap-1.5"><Phone :size="13" /> Telefon</label>
            <input v-model="form.contact_phone" class="input-base w-full" placeholder="+998 …" />
          </div>
          <div>
            <label class="label-base flex items-center gap-1.5"><MapPin :size="13" /> Manzil</label>
            <input v-model="form.contact_address" class="input-base w-full" placeholder="Toshkent, Oʻzbekiston" />
          </div>
        </div>

        <!-- Social -->
        <h3 class="mb-3 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <Share2 :size="13" /> Ijtimoiy tarmoqlar (to'liq URL)
        </h3>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label class="label-base">Telegram</label>
            <input v-model="form.social_telegram" class="input-base w-full font-mono text-xs" placeholder="https://t.me/…" />
          </div>
          <div>
            <label class="label-base">Facebook</label>
            <input v-model="form.social_facebook" class="input-base w-full font-mono text-xs" placeholder="https://facebook.com/…" />
          </div>
          <div>
            <label class="label-base">Instagram</label>
            <input v-model="form.social_instagram" class="input-base w-full font-mono text-xs" placeholder="https://instagram.com/…" />
          </div>
          <div>
            <label class="label-base">YouTube</label>
            <input v-model="form.social_youtube" class="input-base w-full font-mono text-xs" placeholder="https://youtube.com/@…" />
          </div>
          <div>
            <label class="label-base">LinkedIn</label>
            <input v-model="form.social_linkedin" class="input-base w-full font-mono text-xs" placeholder="https://linkedin.com/company/…" />
          </div>
          <div>
            <label class="label-base">X / Twitter</label>
            <input v-model="form.social_twitter" class="input-base w-full font-mono text-xs" placeholder="https://x.com/…" />
          </div>
        </div>
      </section>

      <div class="flex justify-end pb-8">
        <AppButton :loading="saving" @click="save"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
      </div>
    </div>
  </div>
</template>
