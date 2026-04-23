<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, Check, Image as ImageIcon, Loader2, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'

interface BoardMember {
  id: string
  name: string
  title?: string
  role: string
  affiliation?: string
  country?: string
  degree?: string
  specialization?: string
  email?: string
  bio?: string
  orcid_id?: string
  scopus_id?: string
  researcher_id?: string
  google_scholar_url?: string
  website_url?: string
  photo_url?: string
  order: number
  is_active: boolean
}

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const isEdit = computed(() => !!route.params.id)
const memberId = computed(() => route.params.id as string)

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)

const ROLES = ['editor_in_chief', 'associate_editor', 'section_editor', 'reviewer']
const roleLabel: Record<string, string> = {
  editor_in_chief: 'Bosh muharrir',
  associate_editor: "Muharrir o'rinbosari",
  section_editor: "Bo'lim muharriri",
  reviewer: 'Retsenzent',
}

const form = reactive({
  name: '',
  title: '',
  role: 'reviewer',
  affiliation: '',
  country: "O'zbekiston",
  degree: '',
  specialization: '',
  email: '',
  bio: '',
  orcid_id: '',
  scopus_id: '',
  researcher_id: '',
  google_scholar_url: '',
  website_url: '',
  photo_url: '',
  is_active: true,
  order: 0,
})

async function loadMember() {
  loading.value = true
  try {
    // Load from the admin list and pick the one we need (no single-get endpoint)
    const members = await api.get<BoardMember[]>('/api/editorial/members')
    const m = members.find(x => x.id === memberId.value)
    if (!m) { toast.error('Topilmadi'); router.push('/admin/editorial'); return }
    Object.assign(form, {
      name: m.name ?? '',
      title: m.title ?? '',
      role: m.role ?? 'reviewer',
      affiliation: m.affiliation ?? '',
      country: m.country || "O'zbekiston",
      degree: m.degree ?? '',
      specialization: m.specialization ?? '',
      email: m.email ?? '',
      bio: m.bio ?? '',
      orcid_id: m.orcid_id ?? '',
      scopus_id: m.scopus_id ?? '',
      researcher_id: m.researcher_id ?? '',
      google_scholar_url: m.google_scholar_url ?? '',
      website_url: m.website_url ?? '',
      photo_url: m.photo_url ?? '',
      is_active: m.is_active ?? true,
      order: m.order ?? 0,
    })
  } finally { loading.value = false }
}

async function uploadPhoto(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.photo_url = res.s3_key
    toast.success('Rasm yuklandi')
  } catch { toast.error('Rasm yuklanmadi') }
  finally { uploading.value = false }
}

function resolvePhoto(u: string) {
  if (!u) return ''
  return u.startsWith('http') || u.startsWith('/') ? u : `/api/uploads/${u}`
}

async function save() {
  if (!form.name.trim()) { toast.error('Ism kiritilmagan'); return }
  saving.value = true
  try {
    const payload = { ...form }
    if (isEdit.value) {
      await api.put(`/api/editorial/members/${memberId.value}`, payload)
      toast.success('Saqlandi')
    } else {
      await api.post('/api/editorial/members', payload)
      toast.success('Qo\'shildi')
    }
    router.push('/admin/editorial')
  } catch { toast.error('Saqlashda xatolik') }
  finally { saving.value = false }
}

onMounted(() => {
  if (isEdit.value) loadMember()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <!-- Header -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <button
          class="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-700 dark:hover:bg-slate-800"
          @click="router.push('/admin/editorial')"
        >
          <ArrowLeft :size="18" />
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ isEdit ? t('common.edit') : t('admin.editorial.addMember') }}
        </h1>
      </div>
      <AppButton :loading="saving" @click="save">
        <Check :size="15" class="mr-1" />{{ t('common.save') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-20">
      <AppSpinner :size="36" class="text-primary-500" />
    </div>

    <div v-else class="grid grid-cols-1 gap-6 lg:grid-cols-[260px_1fr]">
      <!-- Photo -->
      <section class="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">Rasm</h2>
        <div class="flex flex-col items-center gap-4">
          <div class="h-40 w-40 overflow-hidden rounded-full border-2 border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-900">
            <img
              v-if="form.photo_url"
              :src="resolvePhoto(form.photo_url)"
              class="h-full w-full object-cover"
            />
            <div v-else class="flex h-full w-full items-center justify-center text-slate-300">
              <ImageIcon :size="40" />
            </div>
          </div>
          <label class="flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-700">
            <Loader2 v-if="uploading" :size="14" class="animate-spin" />
            <ImageIcon v-else :size="14" />
            {{ uploading ? 'Yuklanmoqda...' : (form.photo_url ? "Rasm o'zgartirish" : 'Rasm yuklash') }}
            <input type="file" accept="image/*" class="hidden" @change="uploadPhoto" />
          </label>
          <button
            v-if="form.photo_url"
            type="button"
            class="flex items-center gap-1 text-xs text-red-500 hover:underline"
            @click="form.photo_url = ''"
          >
            <X :size="12" />Rasmni olib tashlash
          </button>
          <label class="mt-2 flex w-full cursor-pointer items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
            <input v-model="form.is_active" type="checkbox" class="rounded" />
            {{ t('common.active') }}
          </label>
        </div>
      </section>

      <!-- Main form -->
      <div class="space-y-6">
        <!-- Identity -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Asosiy ma'lumotlar</h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="sm:col-span-2">
              <label class="label-base">To'liq ism *</label>
              <input v-model="form.name" class="input-base w-full" placeholder="Familiya Ism Sharif" />
            </div>
            <div>
              <label class="label-base">Unvon (prefiks)</label>
              <input v-model="form.title" class="input-base w-full" placeholder="Prof., Dr., PhD ..." />
            </div>
            <div>
              <label class="label-base">Ilmiy darajasi</label>
              <input v-model="form.degree" class="input-base w-full" placeholder="PhD, DSc, Akademik ..." />
            </div>
            <div class="sm:col-span-2">
              <label class="label-base">Ixtisoslik / Soha</label>
              <input v-model="form.specialization" class="input-base w-full" placeholder="Masalan: Adabiyotshunoslik" />
            </div>
            <div>
              <label class="label-base">Rol *</label>
              <select v-model="form.role" class="input-base w-full">
                <option v-for="r in ROLES" :key="r" :value="r">{{ roleLabel[r] }}</option>
              </select>
            </div>
            <div>
              <label class="label-base">Tartib raqami</label>
              <input v-model.number="form.order" type="number" class="input-base w-full" />
            </div>
          </div>
        </section>

        <!-- Affiliation & contact -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Tashkilot va aloqa</h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div class="sm:col-span-2">
              <label class="label-base">Tashkilot / Universitet</label>
              <input v-model="form.affiliation" class="input-base w-full" />
            </div>
            <div>
              <label class="label-base">Davlat</label>
              <input v-model="form.country" class="input-base w-full" />
            </div>
            <div>
              <label class="label-base">Email</label>
              <input v-model="form.email" type="email" class="input-base w-full" />
            </div>
          </div>
        </section>

        <!-- Academic identifiers -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Ilmiy identifikatorlar</h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label class="label-base">ORCID</label>
              <input v-model="form.orcid_id" class="input-base w-full font-mono" placeholder="0000-0000-0000-0000" />
            </div>
            <div>
              <label class="label-base">Scopus Author ID</label>
              <input v-model="form.scopus_id" class="input-base w-full font-mono" />
            </div>
            <div>
              <label class="label-base">ResearcherID (Publons)</label>
              <input v-model="form.researcher_id" class="input-base w-full font-mono" />
            </div>
            <div>
              <label class="label-base">Google Scholar URL</label>
              <input v-model="form.google_scholar_url" class="input-base w-full font-mono text-xs" placeholder="https://scholar.google.com/citations?user=..." />
            </div>
            <div class="sm:col-span-2">
              <label class="label-base">Shaxsiy sayt</label>
              <input v-model="form.website_url" class="input-base w-full font-mono text-xs" placeholder="https://..." />
            </div>
          </div>
        </section>

        <!-- Bio -->
        <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
          <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">Biografiya</h2>
          <textarea
            v-model="form.bio"
            rows="6"
            class="input-base w-full resize-y"
            placeholder="Qisqa biografik ma'lumot — sahifada muharrir kartochkasi ochilganda ko'rinadi."
          />
        </section>

        <div class="flex justify-end pb-8">
          <AppButton :loading="saving" @click="save">
            <Check :size="15" class="mr-1" />{{ t('common.save') }}
          </AppButton>
        </div>
      </div>
    </div>
  </div>
</template>
