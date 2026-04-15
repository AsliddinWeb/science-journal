<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, X, Upload, Loader2, Plus } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()
const localeStore = useLocaleStore()

// Route: /admin/conferences/new OR /admin/conferences/:id/edit
// For new: id is undefined, paperId is undefined — this is a NEW paper
// For paper edit: route has conference_id via confId and paperId
// NOTE: This component is used for BOTH:
//   /admin/conferences/new — create new conference paper (user picks conference)
//   /admin/conferences/:id/papers/:paperId/edit — edit existing paper

const confIdFromRoute = computed(() => route.params.id as string | undefined)
const paperId = computed(() => route.params.paperId as string | undefined)
const isEdit = computed(() => !!paperId.value)

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

// Data for dropdowns
const users = ref<{ id: string; full_name: string; email: string }[]>([])
const userSearch = ref('')
const showUserDropdown = ref(false)
const conferences = ref<{ id: string; title: Record<string, string>; sessions: { id: string; title: Record<string, string> }[] }[]>([])

const sessions = computed(() => {
  const conf = conferences.value.find(c => c.id === form.conference_id)
  return conf?.sessions || []
})

// Quick-create conference/session
const showNewConf = ref(false)
const newConfTitle = ref('')
const newConfYear = ref(new Date().getFullYear())
const creatingConf = ref(false)

const showNewSession = ref(false)
const newSessionTitle = ref('')
const creatingSession = ref(false)

async function quickCreateConf() {
  if (!newConfTitle.value) return
  creatingConf.value = true
  try {
    const created = await api.post<any>('/api/admin/conferences', {
      title: { uz: newConfTitle.value }, year: newConfYear.value, is_active: true,
    })
    await loadMeta()
    form.conference_id = created.id
    showNewConf.value = false
    newConfTitle.value = ''
    toast.success("Konferensiya yaratildi")
  } catch { toast.error("Xatolik") }
  finally { creatingConf.value = false }
}

async function quickCreateSession() {
  if (!newSessionTitle.value || !form.conference_id) return
  creatingSession.value = true
  try {
    const created = await api.post<any>(`/api/admin/conferences/${form.conference_id}/sessions`, {
      title: { uz: newSessionTitle.value }, order: sessions.value.length + 1,
    })
    await loadMeta()
    form.session_id = created.id
    showNewSession.value = false
    newSessionTitle.value = ''
    toast.success("Son yaratildi")
  } catch { toast.error("Xatolik") }
  finally { creatingSession.value = false }
}

const STATUSES = ['draft', 'submitted', 'accepted', 'rejected', 'published']

interface CoAuthorForm {
  guest_name: string; guest_email: string; guest_affiliation: string
  guest_orcid: string; is_corresponding: boolean
}

const form = reactive({
  title: { uz: '', ru: '', en: '' },
  abstract: { uz: '', ru: '', en: '' },
  keywords: { uz: '', ru: '', en: '' },
  language: 'uz' as string,
  conference_id: '',
  session_id: '',
  author_id: '',
  author_name: '',
  status: 'draft' as string,
  doi: '',
  published_date: '',
  pages: '',
  pdf_file_path: '',
  pdf_file_size: null as number | null,
  references: '' as string,
  funding: '',
  co_authors: [] as CoAuthorForm[],
})

async function loadPaper() {
  if (!confIdFromRoute.value || !paperId.value) return
  loading.value = true
  try {
    const data = await api.get<any>(`/api/conferences/${confIdFromRoute.value}/papers/${paperId.value}`)
    form.title = { uz: data.title?.uz || '', ru: data.title?.ru || '', en: data.title?.en || '' }
    form.abstract = { uz: data.abstract?.uz || '', ru: data.abstract?.ru || '', en: data.abstract?.en || '' }
    if (Array.isArray(data.keywords)) {
      form.keywords = { uz: data.keywords.join(', '), ru: '', en: '' }
    } else {
      form.keywords = {
        uz: (data.keywords?.uz || []).join(', '),
        ru: (data.keywords?.ru || []).join(', '),
        en: (data.keywords?.en || []).join(', '),
      }
    }
    form.language = data.language
    form.conference_id = data.conference_id || confIdFromRoute.value || ''
    form.session_id = data.session_id || ''
    form.author_id = data.author_id
    form.author_name = data.author?.full_name || ''
    form.status = data.status
    form.doi = data.doi || ''
    form.published_date = data.published_date ? data.published_date.split('T')[0] : ''
    form.pages = data.pages || ''
    form.pdf_file_path = data.pdf_file_path || ''
    form.pdf_file_size = data.pdf_file_size || null
    form.references = (data.references || []).join('\n')
    form.funding = data.funding || ''
    form.co_authors = (data.co_authors || []).map((a: any) => ({
      guest_name: a.guest_name || a.user?.full_name || '',
      guest_email: a.guest_email || '',
      guest_affiliation: a.guest_affiliation || '',
      guest_orcid: a.guest_orcid || '',
      is_corresponding: a.is_corresponding,
    }))
  } catch {
    toast.error('Yuklanmadi')
    router.push('/admin/conferences')
  } finally { loading.value = false }
}

async function loadMeta() {
  try {
    const data = await api.get<{ items: any[] }>('/api/admin/conferences?limit=100')
    conferences.value = data.items
  } catch {}
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
function selectUser(u: { id: string; full_name: string }) { form.author_id = u.id; form.author_name = u.full_name; userSearch.value = ''; users.value = []; showUserDropdown.value = false }

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
    toast.success('PDF yuklandi')
  } catch { toast.error('PDF yuklanmadi') }
  finally { uploading.value = false }
}

async function save() {
  if (!form.author_id) { toast.error("Muallif tanlanmagan"); return }
  if (!form.conference_id) { toast.error("Konferensiya tanlanmagan"); return }
  if (!form.title.uz && !form.title.ru && !form.title.en) { toast.error("Sarlavha kiritilmagan"); return }
  saving.value = true
  try {
    const payload = {
      title: form.title, abstract: form.abstract,
      keywords: {
        uz: form.keywords.uz ? form.keywords.uz.split(',').map(s => s.trim()).filter(Boolean) : [],
        ru: form.keywords.ru ? form.keywords.ru.split(',').map(s => s.trim()).filter(Boolean) : [],
        en: form.keywords.en ? form.keywords.en.split(',').map(s => s.trim()).filter(Boolean) : [],
      },
      language: form.language, session_id: form.session_id || null,
      author_id: form.author_id, status: form.status,
      doi: form.doi || null, published_date: form.published_date || null,
      pages: form.pages || null, pdf_file_path: form.pdf_file_path || null,
      pdf_file_size: form.pdf_file_size || null,
      references: form.references ? form.references.split('\n').map(s => s.trim()).filter(Boolean) : null,
      funding: form.funding || null,
      co_authors: form.co_authors.filter(a => a.guest_name).map((a, i) => ({
        guest_name: a.guest_name, guest_email: a.guest_email || null,
        guest_affiliation: a.guest_affiliation || null, guest_orcid: a.guest_orcid || null,
        order: i + 1, is_corresponding: a.is_corresponding,
      })),
    }
    if (isEdit.value) {
      await api.put(`/api/admin/conferences/${form.conference_id}/papers/${paperId.value}`, payload)
      toast.success("Saqlandi")
    } else {
      await api.post(`/api/admin/conferences/${form.conference_id}/papers`, payload)
      toast.success("Maqola yaratildi")
      router.push('/admin/conferences')
    }
  } catch (e: any) { toast.error(e?.response?.data?.detail || "Xatolik") }
  finally { saving.value = false }
}

onMounted(async () => {
  await loadMeta()
  if (confIdFromRoute.value) form.conference_id = confIdFromRoute.value
  if (isEdit.value) await loadPaper()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="router.push('/admin/conferences')">
          <ArrowLeft :size="16" />{{ t('common.back') }}
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ isEdit ? t('admin.articles.edit') : t('admin.articles.create') }}
        </h1>
      </div>
      <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24"><AppSpinner :size="36" class="text-primary-500" /></div>
    <div v-else class="space-y-6">

      <!-- ── Basic Info — aynan AdminArticleFormView dek ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_basic') }}</h2>
        <div class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <label class="label-base">{{ t('admin.articles.col_status') }}</label>
            <select v-model="form.status" class="input-base w-full">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
            </select>
          </div>
          <div>
            <label class="label-base">Til</label>
            <select v-model="form.language" class="input-base w-full">
              <option value="uz">O'zbek</option><option value="ru">Русский</option><option value="en">English</option>
            </select>
          </div>
          <div>
            <label class="label-base">Chop etilgan sana</label>
            <input v-model="form.published_date" type="date" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">DOI</label>
            <input v-model="form.doi" class="input-base w-full font-mono text-sm" placeholder="10.xxxxx/xxxxx" />
          </div>
        </div>
        <div class="mb-4 grid grid-cols-2 gap-4">
          <div>
            <label class="label-base">Sahifalar</label>
            <input v-model="form.pages" class="input-base w-full" placeholder="82-86" />
          </div>
          <div />
        </div>
        <!-- Author -->
        <div class="mb-4">
          <label class="label-base">{{ t('admin.articles.author') }} *</label>
          <div class="relative">
            <div v-if="form.author_id" class="flex items-center gap-2 rounded-lg border border-primary-300 bg-primary-50 px-3 py-2 dark:border-primary-700 dark:bg-primary-950/30">
              <span class="flex-1 text-sm font-medium text-primary-800 dark:text-primary-300">{{ form.author_name }}</span>
              <button class="text-slate-400 hover:text-red-500" @click="form.author_id = ''; form.author_name = ''"><X :size="15" /></button>
            </div>
            <div v-else>
              <input v-model="userSearch" class="input-base w-full" :placeholder="t('admin.articles.author_search')" @input="onUserSearch" @focus="showUserDropdown = true" />
              <div v-if="users.length" class="absolute z-20 mt-1 w-full rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800">
                <button v-for="u in users" :key="u.id" class="flex w-full flex-col px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700" @click="selectUser(u)">
                  <span class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ u.full_name }}</span>
                  <span class="text-xs text-slate-400">{{ u.email }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <!-- Conference + Session (= Volume + Issue) -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="label-base">{{ t('admin.sidebar.conferences') }} *</label>
            <div class="flex gap-2">
              <select v-model="form.conference_id" class="input-base flex-1" @change="form.session_id = ''">
                <option value="">—</option>
                <option v-for="c in conferences" :key="c.id" :value="c.id">{{ getLocalizedField(c.title, localeStore.current, '') }}</option>
              </select>
              <button type="button" class="shrink-0 rounded-lg border border-primary-300 bg-primary-50 px-3 text-sm font-bold text-primary-700 hover:bg-primary-100 dark:border-primary-700 dark:bg-primary-950 dark:text-primary-300" @click="showNewConf = true">+</button>
            </div>
            <!-- Quick create conference -->
            <div v-if="showNewConf" class="mt-2 rounded-lg border border-primary-200 bg-primary-50 p-3 dark:border-primary-800 dark:bg-primary-950/30">
              <input v-model="newConfTitle" class="input-base mb-2 w-full text-sm" placeholder="Konferensiya nomi" @keyup.enter="quickCreateConf" />
              <div class="flex items-center gap-2">
                <input v-model.number="newConfYear" type="number" class="input-base w-20 text-sm" />
                <AppButton size="sm" :loading="creatingConf" @click="quickCreateConf">{{ t('common.create') }}</AppButton>
                <button type="button" class="text-xs text-slate-500 hover:text-slate-700" @click="showNewConf = false">{{ t('common.cancel') }}</button>
              </div>
            </div>
          </div>
          <div>
            <label class="label-base">{{ t('admin.conferences.sessions') }}</label>
            <div class="flex gap-2">
              <select v-model="form.session_id" class="input-base flex-1" :disabled="!form.conference_id">
                <option value="">—</option>
                <option v-for="s in sessions" :key="s.id" :value="s.id">{{ getLocalizedField(s.title, localeStore.current, '') }}</option>
              </select>
              <button v-if="form.conference_id" type="button" class="shrink-0 rounded-lg border border-primary-300 bg-primary-50 px-3 text-sm font-bold text-primary-700 hover:bg-primary-100 dark:border-primary-700 dark:bg-primary-950 dark:text-primary-300" @click="showNewSession = true">+</button>
            </div>
            <!-- Quick create session -->
            <div v-if="showNewSession" class="mt-2 rounded-lg border border-primary-200 bg-primary-50 p-3 dark:border-primary-800 dark:bg-primary-950/30">
              <input v-model="newSessionTitle" class="input-base mb-2 w-full text-sm" placeholder="Son nomi (masalan: Son 1)" @keyup.enter="quickCreateSession" />
              <div class="flex items-center gap-2">
                <AppButton size="sm" :loading="creatingSession" @click="quickCreateSession">{{ t('common.create') }}</AppButton>
                <button type="button" class="text-xs text-slate-500 hover:text-slate-700" @click="showNewSession = false">{{ t('common.cancel') }}</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Title & Abstract ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_content') }}</h2>
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="rounded-md px-4 py-1.5 text-sm font-medium transition" :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'" @click="langTab = l">{{ l.toUpperCase() }}</button>
        </div>
        <div class="mb-4"><label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label><input v-model="form.title[langTab]" class="input-base w-full text-base" /></div>
        <div class="mb-4"><label class="label-base">{{ t('article.abstract') }} ({{ langTab.toUpperCase() }})</label><textarea v-model="form.abstract[langTab]" rows="6" class="input-base w-full resize-none" /></div>
      </section>

      <!-- ── Keywords ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('article.keywords') }}</h2>
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="rounded-md px-4 py-1.5 text-sm font-medium transition" :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'" @click="langTab = l">{{ l.toUpperCase() }}</button>
        </div>
        <div><label class="label-base">{{ t('article.keywords') }} ({{ langTab.toUpperCase() }})</label><textarea v-model="form.keywords[langTab]" rows="3" class="input-base w-full resize-none" placeholder="kalit1, kalit2, kalit3" /></div>
      </section>

      <!-- ── PDF ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">PDF</h2>
        <div v-if="form.pdf_file_path" class="mb-3 flex items-center gap-3 rounded-lg bg-emerald-50 px-4 py-2.5 dark:bg-emerald-900/20">
          <span class="flex-1 truncate font-mono text-sm text-emerald-700 dark:text-emerald-400">{{ form.pdf_file_path }}</span>
          <button class="text-slate-400 hover:text-red-500" @click="form.pdf_file_path = ''; form.pdf_file_size = null"><X :size="15" /></button>
        </div>
        <label class="flex cursor-pointer items-center gap-3 rounded-xl border-2 border-dashed border-slate-300 px-5 py-4 transition hover:border-primary-400 dark:border-slate-600">
          <Loader2 v-if="uploading" :size="20" class="animate-spin text-primary-500" /><Upload v-else :size="20" class="text-slate-400" />
          <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : t('upload.dragDrop') }}</span>
          <input type="file" accept=".pdf" class="hidden" @change="uploadPdf" />
        </label>
      </section>

      <!-- ── Co-authors ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('author.submit.add_coauthor') }}</h2>
          <button class="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-1.5 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300" @click="addCoAuthor"><Plus :size="13" />{{ t('common.add') }}</button>
        </div>
        <div class="space-y-4">
          <div v-for="(co, i) in form.co_authors" :key="i" class="relative rounded-lg border border-slate-200 p-4 dark:border-slate-700">
            <button class="absolute right-3 top-3 text-slate-300 hover:text-red-500" @click="removeCoAuthor(i)"><X :size="15" /></button>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div class="sm:col-span-2"><label class="label-base">{{ t('auth.full_name') }}</label><input v-model="co.guest_name" class="input-base w-full" /></div>
              <div><label class="label-base">Email</label><input v-model="co.guest_email" class="input-base w-full" type="email" /></div>
              <div><label class="label-base">ORCID</label><input v-model="co.guest_orcid" class="input-base w-full font-mono text-sm" placeholder="0000-0000-0000-0000" /></div>
              <div class="sm:col-span-2"><label class="label-base">{{ t('auth.affiliation') }}</label><input v-model="co.guest_affiliation" class="input-base w-full" /></div>
              <div class="flex items-end pb-2"><label class="flex cursor-pointer items-center gap-2 text-sm text-slate-600 dark:text-slate-300"><input v-model="co.is_corresponding" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />{{ t('author.submit.corresponding') }}</label></div>
            </div>
          </div>
          <p v-if="!form.co_authors.length" class="text-sm text-slate-400">Hammuallif qo'shilmagan</p>
        </div>
      </section>

      <!-- ── References ── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-1 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.references') }}</h2>
        <p class="mb-3 text-xs text-slate-400">{{ t('admin.articles.references_hint') }}</p>
        <textarea v-model="form.references" rows="8" class="input-base w-full resize-y font-mono text-sm" />
      </section>

      <div class="flex justify-end gap-3 pb-8">
        <AppButton variant="secondary" @click="router.push('/admin/conferences')">{{ t('common.cancel') }}</AppButton>
        <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
      </div>
    </div>
  </div>
</template>
