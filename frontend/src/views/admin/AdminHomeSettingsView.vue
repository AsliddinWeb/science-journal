<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Check, Loader2, Image, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'

const { t } = useI18n()
const toast = useToast()

const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const form = ref({
  hero_title: { uz: '', ru: '', en: '' },
  hero_subtitle: { uz: '', ru: '', en: '' },
  hero_issn: '',
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
})

onMounted(async () => {
  try {
    const data = await api.get<any>('/api/home-settings')
    form.value = {
      hero_title: data.hero_title || { uz: '', ru: '', en: '' },
      hero_subtitle: data.hero_subtitle || { uz: '', ru: '', en: '' },
      hero_issn: data.hero_issn || '',
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
    })
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
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.homeSettings.title') }}</h1>
      <AppButton :loading="saving" @click="save"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24"><AppSpinner :size="36" class="text-primary-500" /></div>

    <div v-else class="space-y-6">
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

      <div class="flex justify-end pb-8">
        <AppButton :loading="saving" @click="save"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
      </div>
    </div>
  </div>
</template>
