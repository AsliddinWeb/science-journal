<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ArrowLeft, X, Upload, Loader2, Plus } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import type { Article } from '@/types/article'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()

const isEdit = computed(() => !!route.params.id)
const articleId = computed(() => route.params.id as string)

const loading = ref(false)
const saving = ref(false)
const uploading = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

// Users for author selector
const users = ref<{ id: string; full_name: string; email: string }[]>([])
const userSearch = ref('')
const showUserDropdown = ref(false)

// Categories, volumes, issues
const categories = ref<{ id: string; name: string; name_uz?: string; name_ru?: string; name_en?: string }[]>([])
const volumes = ref<{ id: string; number: number; year: number; issues: { id: string; number: number }[] }[]>([])
const issues = computed(() => {
  if (!form.volume_id) return []
  return volumes.value.find(v => v.id === form.volume_id)?.issues ?? []
})
function volumeLabel(v: { number: number; year: number }) { return `Jild ${v.number} (${v.year})` }
function issueLabel(i: { number: number }) { return `Son ${i.number}` }

const ARTICLE_TYPES = ['research', 'review', 'letter', 'short_communication', 'editorial', 'case_study']
const STATUSES = ['draft', 'submitted', 'under_review', 'revision_required', 'accepted', 'rejected', 'published']

interface CoAuthorForm {
  guest_name: string
  guest_email: string
  guest_affiliation: string
  guest_orcid: string
  is_corresponding: boolean
}

const form = reactive({
  title: { uz: '', ru: '', en: '' },
  abstract: { uz: '', ru: '', en: '' },
  keywords: { uz: '', ru: '', en: '' },
  language: 'uz' as string,
  category_id: '',
  volume_id: '',
  issue_id: '',
  author_id: '',
  author_name: '',
  // "registered" = pick existing user, "guest" = inline author fields
  author_mode: 'registered' as 'registered' | 'guest',
  guest_author_name: '',
  guest_author_email: '',
  guest_author_affiliation: '',
  guest_author_orcid: '',
  status: 'draft' as string,
  doi: '',
  published_date: '',
  pages: '',
  pdf_file_path: '',
  pdf_file_size: null as number | null,
  article_type: '',
  cover_letter: '',
  references: '' as string,
  funding: '',
  conflict_of_interest: '',
  acknowledgments: '',
  co_authors: [] as CoAuthorForm[],
})

// Load article for edit
async function loadArticle() {
  loading.value = true
  try {
    const data = await api.get<Article>(`/api/articles/${articleId.value}`)
    form.title = { uz: data.title.uz || '', ru: data.title.ru || '', en: data.title.en || '' }
    form.abstract = { uz: data.abstract.uz || '', ru: data.abstract.ru || '', en: data.abstract.en || '' }
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
    form.category_id = data.category_id || ''
    form.volume_id = data.volume_id || ''
    form.issue_id = data.issue_id || ''
    form.author_id = data.author_id || ''
    form.author_name = data.author?.full_name || ''
    form.author_mode = data.author_id ? 'registered' : 'guest'

    // In guest mode, extract the primary co-author into guest_author_* fields
    let guestPrimaryId: string | null = null
    if (!data.author_id) {
      const cos = data.co_authors ?? []
      const primary = cos.find(c => c.is_corresponding) ?? cos[0]
      if (primary) {
        const pu = (primary.user as any) ?? {}
        guestPrimaryId = primary.id
        form.guest_author_name = primary.guest_name || pu.full_name || ''
        form.guest_author_email = primary.guest_email || pu.email || ''
        form.guest_author_affiliation = primary.guest_affiliation || pu.affiliation || ''
        form.guest_author_orcid = primary.guest_orcid || pu.orcid_id || ''
      }
    }
    form.status = data.status
    form.doi = data.doi || ''
    form.published_date = data.published_date ? data.published_date.split('T')[0] : ''
    form.pages = data.pages || ''
    form.pdf_file_path = data.pdf_file_path || ''
    form.pdf_file_size = data.pdf_file_size || null
    form.article_type = data.article_type || ''
    form.cover_letter = data.cover_letter || ''
    if (Array.isArray(data.references)) {
      form.references = (data.references || []).join('\n')
    } else if (data.references && typeof data.references === 'object') {
      // Legacy multilingual shape — flatten uz + ru + en into one list
      const r = data.references as any
      form.references = [...(r.uz ?? []), ...(r.ru ?? []), ...(r.en ?? [])].join('\n')
    } else {
      form.references = ''
    }
    form.funding = data.funding || ''
    form.conflict_of_interest = data.conflict_of_interest || ''
    form.acknowledgments = data.acknowledgments || ''
    form.co_authors = data.co_authors.filter(a => a.id !== guestPrimaryId).map(a => ({
      guest_name: a.guest_name || a.user?.full_name || '',
      guest_email: a.guest_email || a.user?.email || '',
      guest_affiliation: a.guest_affiliation || '',
      guest_orcid: a.guest_orcid || '',
      is_corresponding: a.is_corresponding,
    }))
  } catch {
    toast.error('Maqola yuklanmadi')
    router.push('/admin/articles')
  } finally {
    loading.value = false
  }
}

async function loadMeta() {
  try {
    const [cats, vols] = await Promise.all([
      api.get<{ id: string; name: string; name_uz: string; name_ru: string; name_en: string }[]>('/api/categories').catch(() => []),
      api.get<{ id: string; number: number; year: number; issues: { id: string; number: number }[] }[]>('/api/volumes?with_issues=true').catch(() => []),
    ])
    categories.value = cats
    volumes.value = vols
  } catch { /* non-critical */ }
}

async function searchUsers(q: string) {
  if (q.length < 2) { users.value = []; return }
  try {
    const data = await api.get<{ items: { id: string; full_name: string; email: string }[] }>(
      `/api/admin/users?search=${encodeURIComponent(q)}&limit=10`
    )
    users.value = data.items
  } catch { users.value = [] }
}

let userSearchTimer: ReturnType<typeof setTimeout>
function onUserSearch() {
  clearTimeout(userSearchTimer)
  userSearchTimer = setTimeout(() => searchUsers(userSearch.value), 300)
}

function selectUser(u: { id: string; full_name: string; email: string }) {
  form.author_id = u.id
  form.author_name = u.full_name
  userSearch.value = ''
  users.value = []
  showUserDropdown.value = false
}

// Co-authors
function addCoAuthor() {
  form.co_authors.push({ guest_name: '', guest_email: '', guest_affiliation: '', guest_orcid: '', is_corresponding: false })
}
function removeCoAuthor(i: number) { form.co_authors.splice(i, 1) }

// PDF upload
async function uploadPdf(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.type !== 'application/pdf') { toast.error('Faqat PDF fayl'); return }
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string; url: string; file_size: number }>('/api/upload/pdf', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.pdf_file_path = res.s3_key
    form.pdf_file_size = res.file_size
    toast.success('PDF yuklandi')
  } catch { toast.error('PDF yuklanmadi') }
  finally { uploading.value = false }
}

async function save() {
  const guestFilled = !!form.guest_author_name.trim()
  if (form.author_mode === 'registered' && !form.author_id) {
    toast.error("Muallif tanlanmagan"); return
  }
  if (form.author_mode === 'guest' && !guestFilled) {
    toast.error("Mehmon muallif ismini kiriting"); return
  }
  if (!form.title.uz && !form.title.ru && !form.title.en) { toast.error("Sarlavha kiritilmagan"); return }

  saving.value = true
  try {
    // In guest mode, the inline author becomes the corresponding co-author (primary).
    const guestPrimary = form.author_mode === 'guest' && guestFilled
      ? [{
          guest_name: form.guest_author_name.trim(),
          guest_email: form.guest_author_email.trim() || null,
          guest_affiliation: form.guest_author_affiliation.trim() || null,
          guest_orcid: form.guest_author_orcid.trim() || null,
          order: 1,
          is_corresponding: true,
        }]
      : []

    const payload = {
      title: form.title,
      abstract: form.abstract,
      keywords: {
        uz: form.keywords.uz ? form.keywords.uz.split(',').map(s => s.trim()).filter(Boolean) : [],
        ru: form.keywords.ru ? form.keywords.ru.split(',').map(s => s.trim()).filter(Boolean) : [],
        en: form.keywords.en ? form.keywords.en.split(',').map(s => s.trim()).filter(Boolean) : [],
      },
      language: form.language,
      category_id: form.category_id || null,
      volume_id: form.volume_id || null,
      issue_id: form.issue_id || null,
      author_id: form.author_mode === 'registered' ? form.author_id : null,
      status: form.status,
      doi: form.doi || null,
      published_date: form.published_date || null,
      pages: form.pages || null,
      pdf_file_path: form.pdf_file_path || null,
      pdf_file_size: form.pdf_file_size || null,
      article_type: form.article_type || null,
      cover_letter: form.cover_letter || null,
      references: form.references
        ? form.references.split('\n').map(s => s.trim()).filter(Boolean)
        : null,
      funding: form.funding || null,
      conflict_of_interest: form.conflict_of_interest || null,
      acknowledgments: form.acknowledgments || null,
      co_authors: [
        ...guestPrimary,
        ...form.co_authors.filter(a => a.guest_name).map((a, i) => ({
          guest_name: a.guest_name,
          guest_email: a.guest_email || null,
          guest_affiliation: a.guest_affiliation || null,
          guest_orcid: a.guest_orcid || null,
          order: guestPrimary.length + i + 1,
          is_corresponding: a.is_corresponding,
        })),
      ],
    }

    if (isEdit.value) {
      await api.put(`/api/admin/articles/${articleId.value}`, payload)
      toast.success("Saqlandi")
    } else {
      await api.post('/api/admin/articles', payload)
      toast.success("Maqola yaratildi")
      router.push('/admin/articles')
    }
  } catch {
    toast.error("Xatolik yuz berdi")
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  await loadMeta()
  if (isEdit.value) await loadArticle()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button
          class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
          @click="router.push('/admin/articles')"
        >
          <ArrowLeft :size="16" />{{ t('common.back') }}
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ isEdit ? t('admin.articles.edit') : t('admin.articles.create') }}
        </h1>
      </div>
      <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-24">
      <AppSpinner :size="36" class="text-primary-500" />
    </div>

    <div v-else class="space-y-6">

      <!-- ── Basic Info ─────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_basic') }}</h2>

        <div class="mb-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <!-- Status -->
          <div>
            <label class="label-base">{{ t('admin.articles.col_status') }}</label>
            <select v-model="form.status" class="input-base w-full">
              <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
            </select>
          </div>
          <!-- Language -->
          <div>
            <label class="label-base">{{ t('admin.articles.col_language') }}</label>
            <select v-model="form.language" class="input-base w-full">
              <option value="uz">O'zbek</option>
              <option value="ru">Русский</option>
              <option value="en">English</option>
            </select>
          </div>
          <!-- Article type -->
          <div>
            <label class="label-base">{{ t('admin.articles.article_type') }}</label>
            <select v-model="form.article_type" class="input-base w-full">
              <option value="">—</option>
              <option v-for="at in ARTICLE_TYPES" :key="at" :value="at">{{ t(`admin.articles.type_${at}`) }}</option>
            </select>
          </div>
          <!-- DOI -->
          <div>
            <label class="label-base">DOI</label>
            <input v-model="form.doi" class="input-base w-full font-mono text-sm" placeholder="10.xxxxx/xxxxx" />
          </div>
        </div>

        <div class="mb-4 grid grid-cols-2 gap-4">
          <!-- Published date -->
          <div>
            <label class="label-base">Chop etilgan sana</label>
            <input v-model="form.published_date" type="date" class="input-base w-full" />
          </div>
          <!-- Pages -->
          <div>
            <label class="label-base">Sahifalar</label>
            <input v-model="form.pages" class="input-base w-full" placeholder="82-86" />
          </div>
        </div>

        <!-- Author selector -->
        <div class="mb-4">
          <label class="label-base">{{ t('admin.articles.author') }} *</label>

          <!-- Mode toggle -->
          <div class="mb-3 inline-flex rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
            <button
              type="button"
              class="rounded-md px-3 py-1.5 text-xs font-medium transition"
              :class="form.author_mode === 'registered' ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500 hover:text-slate-700'"
              @click="form.author_mode = 'registered'"
            >Ro'yxatdagi foydalanuvchi</button>
            <button
              type="button"
              class="rounded-md px-3 py-1.5 text-xs font-medium transition"
              :class="form.author_mode === 'guest' ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500 hover:text-slate-700'"
              @click="form.author_mode = 'guest'"
            >Mehmon muallif</button>
          </div>

          <!-- Registered user mode -->
          <div v-if="form.author_mode === 'registered'" class="relative">
            <div v-if="form.author_id" class="flex items-center gap-2 rounded-lg border border-primary-300 bg-primary-50 px-3 py-2 dark:border-primary-700 dark:bg-primary-950/30">
              <span class="flex-1 text-sm font-medium text-primary-800 dark:text-primary-300">{{ form.author_name }}</span>
              <button class="text-slate-400 hover:text-red-500" @click="form.author_id = ''; form.author_name = ''">
                <X :size="15" />
              </button>
            </div>
            <div v-else>
              <input
                v-model="userSearch"
                class="input-base w-full"
                :placeholder="t('admin.articles.author_search')"
                @input="onUserSearch"
                @focus="showUserDropdown = true"
              />
              <div v-if="users.length" class="absolute z-20 mt-1 w-full rounded-xl border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800">
                <button
                  v-for="u in users"
                  :key="u.id"
                  class="flex w-full flex-col px-4 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700"
                  @click="selectUser(u)"
                >
                  <span class="text-sm font-medium text-slate-800 dark:text-slate-200">{{ u.full_name }}</span>
                  <span class="text-xs text-slate-400">{{ u.email }}</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Guest inline mode -->
          <div v-else class="rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800/40">
            <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label class="label-base">To'liq ism *</label>
                <input v-model="form.guest_author_name" class="input-base w-full" placeholder="Ism Familiya" />
              </div>
              <div>
                <label class="label-base">Email</label>
                <input v-model="form.guest_author_email" type="email" class="input-base w-full" />
              </div>
              <div class="sm:col-span-2">
                <label class="label-base">Affiliation</label>
                <input v-model="form.guest_author_affiliation" class="input-base w-full" placeholder="Tashkilot / Universitet" />
              </div>
              <div class="sm:col-span-2">
                <label class="label-base">ORCID</label>
                <input v-model="form.guest_author_orcid" class="input-base w-full font-mono" placeholder="0000-0000-0000-0000" />
              </div>
            </div>
            <p class="mt-3 text-[11px] text-slate-400">
              Ushbu muallif tizimda foydalanuvchi sifatida ro'yxatdan o'tmasdan maqolaga biriktiriladi (corresponding muallif sifatida).
            </p>
          </div>
        </div>

        <!-- Category / Volume / Issue -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label class="label-base">{{ t('admin.articles.category') }}</label>
            <select v-model="form.category_id" class="input-base w-full">
              <option value="">—</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name_uz || c.name }}</option>
            </select>
            <p v-if="!categories.length" class="mt-1 text-xs text-slate-400">Kategoriyalar yo'q (Admin → Kategoriyalar da qo'shing)</p>
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.volume') }}</label>
            <select v-model="form.volume_id" class="input-base w-full" @change="form.issue_id = ''">
              <option value="">—</option>
              <option v-for="v in volumes" :key="v.id" :value="v.id">{{ volumeLabel(v) }}</option>
            </select>
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.issue') }}</label>
            <select v-model="form.issue_id" class="input-base w-full" :disabled="!form.volume_id">
              <option value="">—</option>
              <option v-for="iss in issues" :key="iss.id" :value="iss.id">{{ issueLabel(iss) }}</option>
            </select>
          </div>
        </div>
      </section>

      <!-- ── Title & Abstract ───────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_content') }}</h2>

        <!-- Lang tabs -->
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button
            v-for="lang in (['uz', 'ru', 'en'] as const)"
            :key="lang"
            class="rounded-md px-4 py-1.5 text-sm font-medium transition"
            :class="langTab === lang ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500 hover:text-slate-700'"
            @click="langTab = lang"
          >{{ lang.toUpperCase() }}</button>
        </div>

        <div class="mb-4">
          <label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label>
          <input v-model="form.title[langTab]" class="input-base w-full text-base" :placeholder="`Sarlavha (${langTab})`" />
        </div>

        <div>
          <label class="label-base">{{ t('article.abstract') }} ({{ langTab.toUpperCase() }})</label>
          <textarea
            v-model="form.abstract[langTab]"
            rows="6"
            class="input-base w-full resize-none"
            :placeholder="`Annotatsiya (${langTab})...`"
          />
        </div>
      </section>

      <!-- ── Keywords ───────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('article.keywords') }}</h2>

        <!-- Lang tabs for keywords -->
        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button
            v-for="lang in (['uz', 'ru', 'en'] as const)"
            :key="lang"
            class="rounded-md px-4 py-1.5 text-sm font-medium transition"
            :class="langTab === lang ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500 hover:text-slate-700'"
            @click="langTab = lang"
          >{{ lang.toUpperCase() }}</button>
        </div>

        <div>
          <label class="label-base">{{ t('article.keywords') }} ({{ langTab.toUpperCase() }})</label>
          <textarea
            v-model="form.keywords[langTab]"
            rows="3"
            class="input-base w-full resize-none"
            :placeholder="`Kalit so'zlar vergul bilan ajratilgan (${langTab})...`"
          />
        </div>
      </section>

      <!-- ── PDF Upload ─────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">PDF</h2>
        <div v-if="form.pdf_file_path" class="mb-3 flex items-center gap-3 rounded-lg bg-emerald-50 px-4 py-2.5 dark:bg-emerald-900/20">
          <span class="flex-1 truncate font-mono text-sm text-emerald-700 dark:text-emerald-400">{{ form.pdf_file_path }}</span>
          <button class="text-slate-400 hover:text-red-500" @click="form.pdf_file_path = ''; form.pdf_file_size = null"><X :size="15" /></button>
        </div>
        <label class="flex cursor-pointer items-center gap-3 rounded-xl border-2 border-dashed border-slate-300 px-5 py-4 transition hover:border-primary-400 dark:border-slate-600">
          <Loader2 v-if="uploading" :size="20" class="animate-spin text-primary-500" />
          <Upload v-else :size="20" class="text-slate-400" />
          <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : t('upload.dragDrop') }}</span>
          <input type="file" accept=".pdf" class="hidden" @change="uploadPdf" />
        </label>
        <div v-if="form.pdf_file_path" class="mt-2">
          <label class="label-base">PDF URL (qo'lda kiritish)</label>
          <input v-model="form.pdf_file_path" class="input-base w-full font-mono text-sm" />
        </div>
      </section>

      <!-- ── Co-authors ─────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('author.submit.add_coauthor') }}</h2>
          <button
            class="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-1.5 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300"
            @click="addCoAuthor"
          >
            <Plus :size="13" />{{ t('common.add') }}
          </button>
        </div>
        <div class="space-y-4">
          <div
            v-for="(co, i) in form.co_authors"
            :key="i"
            class="relative rounded-lg border border-slate-200 p-4 dark:border-slate-700"
          >
            <button class="absolute right-3 top-3 text-slate-300 hover:text-red-500" @click="removeCoAuthor(i)"><X :size="15" /></button>
            <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div class="sm:col-span-2">
                <label class="label-base">{{ t('auth.full_name') }}</label>
                <input v-model="co.guest_name" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">Email</label>
                <input v-model="co.guest_email" class="input-base w-full" type="email" />
              </div>
              <div>
                <label class="label-base">ORCID</label>
                <input v-model="co.guest_orcid" class="input-base w-full font-mono text-sm" placeholder="0000-0000-0000-0000" />
              </div>
              <div class="sm:col-span-2">
                <label class="label-base">{{ t('auth.affiliation') }}</label>
                <input v-model="co.guest_affiliation" class="input-base w-full" />
              </div>
              <div class="flex items-end pb-2">
                <label class="flex cursor-pointer items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
                  <input v-model="co.is_corresponding" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />
                  {{ t('author.submit.corresponding') }}
                </label>
              </div>
            </div>
          </div>
          <p v-if="!form.co_authors.length" class="text-sm text-slate-400">Hammuallif qo'shilmagan</p>
        </div>
      </section>

      <!-- ── References ─────────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-1 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.references') }}</h2>
        <p class="mb-3 text-xs text-slate-400">{{ t('admin.articles.references_hint') }}</p>
        <textarea
          v-model="form.references"
          rows="8"
          class="input-base w-full resize-y font-mono text-sm"
          placeholder="[1] Ivanov I.I. Title of article. Journal Name. 2024;1(1):1-10.&#10;[2] Smith J. Another reference..."
        />
      </section>

      <!-- ── Extra Fields ───────────────────────────────────── -->
      <section class="rounded-xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h2 class="mb-4 text-sm font-semibold uppercase tracking-wider text-slate-500">{{ t('admin.articles.section_extra') }}</h2>
        <div class="space-y-4">
          <div>
            <label class="label-base">{{ t('admin.articles.funding') }}</label>
            <textarea v-model="form.funding" rows="2" class="input-base w-full resize-none" :placeholder="t('admin.articles.funding_hint')" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.conflict_of_interest') }}</label>
            <textarea v-model="form.conflict_of_interest" rows="2" class="input-base w-full resize-none" :placeholder="t('admin.articles.coi_hint')" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.acknowledgments') }}</label>
            <textarea v-model="form.acknowledgments" rows="2" class="input-base w-full resize-none" :placeholder="t('admin.articles.acknowledgments_hint')" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.articles.cover_letter') }}</label>
            <textarea v-model="form.cover_letter" rows="4" class="input-base w-full resize-none" :placeholder="t('admin.articles.cover_letter_hint')" />
          </div>
        </div>
      </section>

      <!-- Save button -->
      <div class="flex justify-end gap-3 pb-8">
        <AppButton variant="secondary" @click="router.push('/admin/articles')">{{ t('common.cancel') }}</AppButton>
        <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
      </div>

    </div>
  </div>
</template>
