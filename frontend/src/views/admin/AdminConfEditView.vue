<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, Upload, Loader2, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const confId = computed(() => route.params.id as string | undefined)
const isEdit = computed(() => !!confId.value)

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const form = reactive({
  title: { uz: '', ru: '', en: '' } as Record<string, string>,
  description: { uz: '', ru: '', en: '' } as Record<string, string>,
  year: new Date().getFullYear(),
  start_date: '',
  end_date: '',
  location: '',
  organizer: '',
  website_url: '',
  cover_image_url: '',
  is_active: true,
})

async function load() {
  if (!confId.value) return
  loading.value = true
  try {
    const data = await api.get<any>(`/api/admin/conferences?limit=100`)
    const conf = (data.items || []).find((c: any) => c.id === confId.value)
    if (!conf) { toast.error('Topilmadi'); router.push('/admin/conf/list'); return }
    form.title = { uz: conf.title?.uz || '', ru: conf.title?.ru || '', en: conf.title?.en || '' }
    form.description = {
      uz: conf.description?.uz || '',
      ru: conf.description?.ru || '',
      en: conf.description?.en || '',
    }
    form.year = conf.year
    form.start_date = conf.start_date || ''
    form.end_date = conf.end_date || ''
    form.location = conf.location || ''
    form.organizer = conf.organizer || ''
    form.website_url = conf.website_url || ''
    form.cover_image_url = conf.cover_image_url || ''
    form.is_active = !!conf.is_active
  } catch {
    toast.error('Yuklanmadi')
  } finally { loading.value = false }
}

async function uploadCover(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData(); fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.cover_image_url = res.s3_key
    toast.success('Rasm yuklandi')
  } catch { toast.error('Yuklanmadi') }
  finally { uploading.value = false }
}

function coverUrl(key: string) {
  if (!key) return ''
  return key.startsWith('/') || key.startsWith('http') ? key : `/api/uploads/${key}`
}

async function save() {
  if (!form.title.uz && !form.title.ru && !form.title.en) {
    toast.error('Sarlavha kiritilmagan'); return
  }
  saving.value = true
  try {
    const payload: any = {
      title: form.title,
      description: form.description,
      year: form.year,
      start_date: form.start_date || null,
      end_date: form.end_date || null,
      location: form.location || null,
      organizer: form.organizer || null,
      website_url: form.website_url || null,
      cover_image_url: form.cover_image_url || null,
      is_active: form.is_active,
    }
    if (isEdit.value) {
      await api.put(`/api/admin/conferences/${confId.value}`, payload)
      toast.success(t('admin.conferences.updated'))
    } else {
      await api.post('/api/admin/conferences', payload)
      toast.success(t('admin.conferences.created'))
    }
    router.push('/admin/conf/list')
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Xatolik')
  } finally { saving.value = false }
}

onMounted(load)
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="router.push('/admin/conf/list')">
          <ArrowLeft :size="16" />{{ t('common.back') }}
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ isEdit ? t('admin.conferences.edit') : t('admin.conferences.create') }}
        </h1>
      </div>
      <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24"><AppSpinner :size="36" class="text-primary-500" /></div>
    <div v-else class="space-y-6">

      <!-- Meta -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_basic') }}</h2>
        <div class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <label class="label-base">Yil *</label>
            <input v-model.number="form.year" type="number" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">Boshlanish sanasi</label>
            <input v-model="form.start_date" type="date" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">Tugash sanasi</label>
            <input v-model="form.end_date" type="date" class="input-base w-full" />
          </div>
          <div class="flex items-end">
            <label class="flex cursor-pointer items-center gap-2 text-sm text-slate-700 dark:text-slate-200">
              <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />
              {{ t('common.active') }}
            </label>
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label-base">{{ t('admin.conferences.location') }}</label>
            <input v-model="form.location" class="input-base w-full" placeholder="Toshkent, O'zbekiston" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.conferences.organizer') }}</label>
            <input v-model="form.organizer" class="input-base w-full" />
          </div>
          <div class="sm:col-span-2">
            <label class="label-base">{{ t('admin.conferences.website') }}</label>
            <input v-model="form.website_url" class="input-base w-full font-mono text-sm" placeholder="https://..." />
          </div>
        </div>
      </section>

      <!-- Title & Description -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_content') }}</h2>
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l"
                  class="rounded-md px-4 py-1.5 text-sm font-medium transition"
                  :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'"
                  @click="langTab = l">{{ l.toUpperCase() }}</button>
        </div>
        <div class="mb-4">
          <label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label>
          <input v-model="form.title[langTab]" class="input-base w-full text-base" />
        </div>
        <div>
          <label class="label-base">{{ t('article.abstract') }} ({{ langTab.toUpperCase() }})</label>
          <textarea v-model="form.description[langTab]" rows="5" class="input-base w-full resize-none" />
        </div>
      </section>

      <!-- Cover -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.conferences.cover_image') }}</h2>
        <p class="mb-3 text-xs text-slate-400">{{ t('admin.conferences.cover_image_hint') }}</p>
        <div v-if="form.cover_image_url" class="mb-3 flex items-start gap-3">
          <img :src="coverUrl(form.cover_image_url)" class="h-32 w-24 rounded-lg border border-slate-200 object-cover dark:border-slate-700" />
          <button class="rounded-full bg-slate-100 p-1.5 text-slate-500 hover:bg-red-50 hover:text-red-500 dark:bg-slate-700" @click="form.cover_image_url = ''">
            <X :size="14" />
          </button>
        </div>
        <label class="flex cursor-pointer items-center gap-3 rounded-xl border-2 border-dashed border-slate-300 px-5 py-4 transition hover:border-primary-400 dark:border-slate-600">
          <Loader2 v-if="uploading" :size="20" class="animate-spin text-primary-500" />
          <Upload v-else :size="20" class="text-slate-400" />
          <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : t('upload.dragDrop') }}</span>
          <input type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="uploadCover" />
        </label>
      </section>

      <div class="flex justify-end gap-3 pb-8">
        <AppButton variant="secondary" @click="router.push('/admin/conf/list')">{{ t('common.cancel') }}</AppButton>
        <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
      </div>
    </div>
  </div>
</template>
