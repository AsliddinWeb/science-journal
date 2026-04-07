<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, Plus, X, Upload, Loader2, Image } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import type { ConferencePaper, Conference } from '@/types/conference'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const confId = computed(() => route.params.id as string)
const paperId = computed(() => route.params.paperId as string)
const isEdit = computed(() => !!paperId.value)

const conference = ref<Conference | null>(null)
const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const uploadingImage = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const users = ref<{ id: string; full_name: string; email: string }[]>([])
const userSearch = ref('')

const STATUSES = ['draft', 'submitted', 'accepted', 'rejected', 'published']

const form = reactive({
  title: { uz: '', ru: '', en: '' },
  abstract: { uz: '', ru: '', en: '' },
  keywords: [] as string[],
  language: 'uz',
  session_id: '',
  author_id: '',
  author_name: '',
  status: 'draft',
  doi: '',
  pdf_file_path: '',
  pdf_file_size: null as number | null,
  cover_image_url: '',
  references: '',
  funding: '',
  co_authors: [] as { guest_name: string; guest_email: string; guest_affiliation: string; guest_orcid: string; is_corresponding: boolean }[],
})

const keywordInput = ref('')
const sessions = computed(() => conference.value?.sessions || [])

async function loadPaper() {
  loading.value = true
  try {
    const data = await api.get<ConferencePaper>(`/api/conferences/${confId.value}/papers/${paperId.value}`)
    form.title = { uz: data.title.uz || '', ru: data.title.ru || '', en: data.title.en || '' }
    form.abstract = { uz: data.abstract.uz || '', ru: data.abstract.ru || '', en: data.abstract.en || '' }
    form.keywords = data.keywords || []
    form.language = data.language
    form.session_id = data.session_id || ''
    form.author_id = data.author_id
    form.author_name = data.author?.full_name || ''
    form.status = data.status
    form.doi = data.doi || ''
    form.pdf_file_path = data.pdf_file_path || ''
    form.pdf_file_size = data.pdf_file_size || null
    form.cover_image_url = data.cover_image_url || ''
    form.references = (data.references || []).join('\n')
    form.funding = data.funding || ''
    form.co_authors = data.co_authors.map(a => ({
      guest_name: a.guest_name || a.user?.full_name || '',
      guest_email: a.guest_email || a.user?.email || '',
      guest_affiliation: a.guest_affiliation || '',
      guest_orcid: a.guest_orcid || '',
      is_corresponding: a.is_corresponding,
    }))
  } catch { toast.error("Yuklanmadi"); router.back() }
  finally { loading.value = false }
}

async function searchUsers(q: string) {
  if (q.length < 2) { users.value = []; return }
  try {
    const data = await api.get<{ items: { id: string; full_name: string; email: string }[] }>(`/api/admin/users?search=${encodeURIComponent(q)}&limit=10`)
    users.value = data.items
  } catch { users.value = [] }
}

let userSearchTimer: ReturnType<typeof setTimeout>
function onUserSearch() { clearTimeout(userSearchTimer); userSearchTimer = setTimeout(() => searchUsers(userSearch.value), 300) }
function selectUser(u: { id: string; full_name: string }) { form.author_id = u.id; form.author_name = u.full_name; userSearch.value = ''; users.value = [] }

function addKeyword() { const kw = keywordInput.value.trim(); if (kw && !form.keywords.includes(kw)) form.keywords.push(kw); keywordInput.value = '' }
function removeKeyword(i: number) { form.keywords.splice(i, 1) }
function addCoAuthor() { form.co_authors.push({ guest_name: '', guest_email: '', guest_affiliation: '', guest_orcid: '', is_corresponding: false }) }
function removeCoAuthor(i: number) { form.co_authors.splice(i, 1) }

async function uploadPdf(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData(); fd.append('file', file)
    const res = await api.post<{ s3_key: string; file_size: number }>('/api/upload/pdf', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.pdf_file_path = res.s3_key; form.pdf_file_size = res.file_size
  } catch { toast.error("PDF yuklanmadi") }
  finally { uploading.value = false }
}

async function uploadImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingImage.value = true
  try {
    const fd = new FormData(); fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.cover_image_url = res.s3_key
  } catch { toast.error("Rasm yuklanmadi") }
  finally { uploadingImage.value = false }
}

async function save() {
  if (!form.author_id) { toast.error("Muallif tanlanmagan"); return }
  if (!form.title.uz && !form.title.ru && !form.title.en) { toast.error("Sarlavha kiriting"); return }

  saving.value = true
  try {
    const payload = {
      title: form.title,
      abstract: form.abstract,
      keywords: form.keywords,
      language: form.language,
      session_id: form.session_id || null,
      author_id: form.author_id,
      status: form.status,
      doi: form.doi || null,
      pdf_file_path: form.pdf_file_path || null,
      pdf_file_size: form.pdf_file_size || null,
      cover_image_url: form.cover_image_url || null,
      references: form.references ? form.references.split('\n').map(s => s.trim()).filter(Boolean) : null,
      funding: form.funding || null,
      co_authors: form.co_authors.filter(a => a.guest_name).map((a, i) => ({ ...a, order: i + 1 })),
    }

    if (isEdit.value) {
      await api.put(`/api/admin/conferences/${confId.value}/papers/${paperId.value}`, payload)
      toast.success(t('admin.conferences.updated'))
    } else {
      await api.post(`/api/admin/conferences/${confId.value}/papers`, payload)
      toast.success(t('admin.conferences.created'))
      router.push(`/admin/conferences/${confId.value}/papers`)
    }
  } catch { toast.error("Xatolik") }
  finally { saving.value = false }
}

onMounted(async () => {
  try { conference.value = await api.get<Conference>(`/api/conferences/${confId.value}`) } catch {}
  if (isEdit.value) await loadPaper()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="router.push(`/admin/conferences/${confId}/papers`)">
          <ArrowLeft :size="16" />{{ t('common.back') }}
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ isEdit ? t('admin.conferences.paper_edit') : t('admin.conferences.paper_create') }}
        </h1>
      </div>
      <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24"><AppSpinner :size="36" class="text-primary-500" /></div>

    <div v-else class="space-y-6">
      <!-- Basic info -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_basic') }}</h2>
        <div class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
          <div>
            <label class="label-base">{{ t('admin.articles.col_status') }}</label>
            <select v-model="form.status" class="input-base w-full">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
            </select>
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.col_language') }}</label>
            <select v-model="form.language" class="input-base w-full">
              <option value="uz">O'zbek</option><option value="ru">Русский</option><option value="en">English</option>
            </select>
          </div>
          <div>
            <label class="label-base">DOI</label>
            <input v-model="form.doi" class="input-base w-full font-mono text-sm" placeholder="10.xxxxx/xxxxx" />
          </div>
        </div>
        <!-- Author -->
        <div class="mb-4">
          <label class="label-base">{{ t('admin.articles.author') }} *</label>
          <div v-if="form.author_id" class="flex items-center gap-2 rounded-lg border border-primary-300 bg-primary-50 px-3 py-2 dark:border-primary-700 dark:bg-primary-950/30">
            <span class="flex-1 text-sm font-medium text-primary-800 dark:text-primary-300">{{ form.author_name }}</span>
            <button class="text-slate-400 hover:text-red-500" @click="form.author_id = ''; form.author_name = ''"><X :size="15" /></button>
          </div>
          <div v-else class="relative">
            <input v-model="userSearch" class="input-base w-full" :placeholder="t('admin.articles.author_search')" @input="onUserSearch" />
            <div v-if="users.length" class="absolute z-20 mt-1 w-full rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800">
              <button v-for="u in users" :key="u.id" class="flex w-full flex-col px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700" @click="selectUser(u)">
                <span class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ u.full_name }}</span>
                <span class="text-xs text-slate-400">{{ u.email }}</span>
              </button>
            </div>
          </div>
        </div>
        <!-- Session -->
        <div>
          <label class="label-base">{{ t('admin.conferences.sessions') }}</label>
          <select v-model="form.session_id" class="input-base w-full">
            <option value="">—</option>
            <option v-for="sess in sessions" :key="sess.id" :value="sess.id">{{ sess.title.uz || sess.title.en || sess.title.ru }}</option>
          </select>
        </div>
      </section>

      <!-- Title & Abstract -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_content') }}</h2>
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="rounded-md px-4 py-1.5 text-sm font-medium transition" :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'" @click="langTab = l">{{ l.toUpperCase() }}</button>
        </div>
        <div class="mb-4"><label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label><input v-model="form.title[langTab]" class="input-base w-full text-base" /></div>
        <div><label class="label-base">{{ t('article.abstract') }} ({{ langTab.toUpperCase() }})</label><textarea v-model="form.abstract[langTab]" rows="5" class="input-base w-full resize-none" /></div>
      </section>

      <!-- Keywords -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('article.keywords') }}</h2>
        <div class="mb-3 flex flex-wrap gap-2">
          <span v-for="(kw, i) in form.keywords" :key="i" class="flex items-center gap-1 rounded-full bg-primary-100 px-3 py-1 text-sm font-medium text-primary-800 dark:bg-primary-900/40 dark:text-primary-300">
            {{ kw }}<button class="ml-0.5 text-primary-400 hover:text-primary-700" @click="removeKeyword(i)"><X :size="12" /></button>
          </span>
        </div>
        <div class="flex gap-2">
          <input v-model="keywordInput" class="input-base flex-1" placeholder="Kalit so'z..." @keyup.enter="addKeyword" />
          <AppButton variant="secondary" @click="addKeyword"><Plus :size="15" /></AppButton>
        </div>
      </section>

      <!-- PDF + Cover image -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="grid gap-6 sm:grid-cols-2">
          <div>
            <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">PDF</h2>
            <div v-if="form.pdf_file_path" class="mb-2 flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 dark:bg-emerald-900/20">
              <span class="flex-1 truncate font-mono text-xs text-emerald-700 dark:text-emerald-400">{{ form.pdf_file_path }}</span>
              <button class="text-slate-400 hover:text-red-500" @click="form.pdf_file_path = ''; form.pdf_file_size = null"><X :size="14" /></button>
            </div>
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border-2 border-dashed border-slate-300 px-4 py-3 hover:border-primary-400 dark:border-slate-600">
              <Loader2 v-if="uploading" :size="18" class="animate-spin text-primary-500" /><Upload v-else :size="18" class="text-slate-400" />
              <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : 'PDF yuklash' }}</span>
              <input type="file" accept=".pdf" class="hidden" @change="uploadPdf" />
            </label>
          </div>
          <div>
            <h2 class="mb-3 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.conferences.cover_image') }}</h2>
            <div v-if="form.cover_image_url" class="mb-2">
              <img :src="`/api/uploads/${form.cover_image_url}`" class="h-24 w-full rounded-lg object-cover" />
              <button class="mt-1 text-xs text-red-500 hover:underline" @click="form.cover_image_url = ''">{{ t('common.delete') }}</button>
            </div>
            <label class="flex cursor-pointer items-center gap-2 rounded-xl border-2 border-dashed border-slate-300 px-4 py-3 hover:border-primary-400 dark:border-slate-600">
              <Loader2 v-if="uploadingImage" :size="18" class="animate-spin text-primary-500" /><Image v-else :size="18" class="text-slate-400" />
              <span class="text-sm text-slate-500">{{ uploadingImage ? 'Yuklanmoqda...' : t('admin.conferences.cover_image_hint') }}</span>
              <input type="file" accept="image/*" class="hidden" @change="uploadImage" />
            </label>
          </div>
        </div>
      </section>

      <!-- Co-authors -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('author.submit.add_coauthor') }}</h2>
          <button class="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-1.5 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300" @click="addCoAuthor"><Plus :size="13" />{{ t('common.add') }}</button>
        </div>
        <div class="space-y-3">
          <div v-for="(co, i) in form.co_authors" :key="i" class="relative rounded-lg border border-slate-200 p-3 dark:border-slate-700">
            <button class="absolute right-2 top-2 text-slate-300 hover:text-red-500" @click="removeCoAuthor(i)"><X :size="14" /></button>
            <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
              <div class="sm:col-span-2"><input v-model="co.guest_name" class="input-base w-full text-sm" :placeholder="t('auth.full_name')" /></div>
              <div><input v-model="co.guest_email" class="input-base w-full text-sm" placeholder="Email" /></div>
              <div><input v-model="co.guest_affiliation" class="input-base w-full text-sm" :placeholder="t('auth.affiliation')" /></div>
            </div>
          </div>
          <p v-if="!form.co_authors.length" class="text-sm text-slate-400">Hammuallif qo'shilmagan</p>
        </div>
      </section>

      <!-- References -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-1 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.references') }}</h2>
        <p class="mb-3 text-xs text-slate-400">{{ t('admin.articles.references_hint') }}</p>
        <textarea v-model="form.references" rows="6" class="input-base w-full resize-y font-mono text-sm" placeholder="[1] Muallif. Sarlavha. Jurnal..." />
      </section>

      <div class="flex justify-end gap-3 pb-8">
        <AppButton variant="secondary" @click="router.push(`/admin/conferences/${confId}/papers`)">{{ t('common.cancel') }}</AppButton>
        <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
      </div>
    </div>
  </div>
</template>
