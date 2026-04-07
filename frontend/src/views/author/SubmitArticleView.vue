<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  CheckCircle, ChevronRight, ChevronLeft, Save,
  Send, AlertCircle, X, Plus, Tag,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import PdfUploadZone from '@/components/upload/PdfUploadZone.vue'
import CoAuthorModal from '@/components/author/CoAuthorModal.vue'
import AuthorRow from '@/components/author/AuthorRow.vue'
import type { CoAuthorEntry } from '@/components/author/CoAuthorModal.vue'
import type { AuthorEntry } from '@/components/author/AuthorRow.vue'

const { t } = useI18n()
const router = useRouter()
const authStore = useAuthStore()

// ─── Step management ────────────────────────────────────────────────
const STEPS = ['step1', 'step2', 'step3', 'step4'] as const
type StepKey = typeof STEPS[number]
const currentStep = ref(0)

// ─── Draft restore ───────────────────────────────────────────────────
const DRAFT_KEY = 'submit_article_draft'
const showRestoreBanner = ref(false)

function saveDraft() {
  localStorage.setItem(DRAFT_KEY, JSON.stringify({
    step1: step1,
    step2: authors.value.filter((a) => !a.readonly),
    step3: step3,
    savedAt: new Date().toISOString(),
  }))
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY)
  showRestoreBanner.value = false
}

function restoreDraft() {
  const raw = localStorage.getItem(DRAFT_KEY)
  if (!raw) return
  try {
    const data = JSON.parse(raw)
    if (data.step1) Object.assign(step1, data.step1)
    if (data.step3) Object.assign(step3, data.step3)
    if (data.step2?.length) {
      authors.value = [authors.value[0], ...data.step2]
    }
  } catch {}
  showRestoreBanner.value = false
}

onMounted(() => {
  const draft = localStorage.getItem(DRAFT_KEY)
  if (draft) showRestoreBanner.value = true
})

let draftTimer: ReturnType<typeof setInterval>
onMounted(() => { draftTimer = setInterval(saveDraft, 30_000) })
onUnmounted(() => clearInterval(draftTimer))

// ─── Step 1 — Article info ───────────────────────────────────────────
const titleTab = ref<'uz' | 'ru' | 'en'>('uz')
const abstractTab = ref<'uz' | 'ru' | 'en'>('uz')

const step1 = reactive({
  title: { uz: '', ru: '', en: '' },
  abstract: { uz: '', ru: '', en: '' },
  keywords: [] as string[],
  keywordInput: '',
  language: 'uz' as 'uz' | 'ru' | 'en',
  category_id: '',
})

const categories = ref<{ id: string; name_uz: string; name_ru: string; name_en: string }[]>([])
const categoriesLoading = ref(true)

onMounted(async () => {
  try {
    categories.value = await api.get('/api/categories')
  } finally {
    categoriesLoading.value = false
  }
})

function addKeyword() {
  const kw = step1.keywordInput.trim()
  if (kw && !step1.keywords.includes(kw)) step1.keywords.push(kw)
  step1.keywordInput = ''
}

function removeKeyword(kw: string) {
  step1.keywords = step1.keywords.filter((k) => k !== kw)
}

function onKeywordKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault()
    addKeyword()
  }
}

// ─── Step 1 validation ───────────────────────────────────────────────
const step1Errors = reactive({ title: '', abstract: '', keywords: '', language: '' })

function validateStep1(): boolean {
  step1Errors.title = ''
  step1Errors.abstract = ''
  step1Errors.keywords = ''
  let ok = true
  const titleValues = Object.values(step1.title).filter(Boolean)
  if (titleValues.length === 0 || titleValues.every((v) => v.length < 10)) {
    step1Errors.title = t('author.submit.validation.title_min')
    ok = false
  }
  const absValues = Object.values(step1.abstract).filter(Boolean)
  if (absValues.length === 0 || absValues.every((v) => v.length < 100)) {
    step1Errors.abstract = t('author.submit.validation.abstract_min')
    ok = false
  }
  if (step1.keywords.length < 3) {
    step1Errors.keywords = t('author.submit.validation.keywords_min')
    ok = false
  }
  return ok
}

// ─── Step 2 — Authors ────────────────────────────────────────────────
const uuidv4 = () => crypto.randomUUID()

const user = computed(() => authStore.user)
const authors = ref<AuthorEntry[]>([
  {
    id: uuidv4(),
    user_id: user.value?.id,
    name: user.value?.full_name ?? '',
    email: user.value?.email,
    affiliation: user.value?.affiliation ?? '',
    country: user.value?.country ?? '',
    orcid: user.value?.orcid_id ?? null,
    is_corresponding: true,
    readonly: true,
  },
])
const showCoAuthorModal = ref(false)

function addCoAuthor(entry: CoAuthorEntry) {
  authors.value.push({
    id: uuidv4(),
    user_id: entry.user_id,
    name: entry.guest_name ?? '',
    email: entry.guest_email,
    affiliation: entry.guest_affiliation,
    country: entry.guest_country,
    orcid: entry.guest_orcid,
    is_corresponding: false,
    readonly: false,
  })
}

function removeAuthor(id: string) {
  authors.value = authors.value.filter((a) => a.id !== id)
}

function toggleCorresponding(id: string) {
  authors.value.forEach((a) => { a.is_corresponding = a.id === id })
}

// ─── Step 3 — PDF upload ─────────────────────────────────────────────
const step3 = reactive({
  pdfKey: null as string | null,
  pdfName: null as string | null,
  pdfSize: null as number | null,
  coverLetter: '',
})

const step3Errors = reactive({ pdf: '' })

function validateStep3(): boolean {
  step3Errors.pdf = ''
  if (!step3.pdfKey) {
    step3Errors.pdf = t('author.submit.validation.pdf_required')
    return false
  }
  return true
}

// ─── Step 4 — Review & Submit ────────────────────────────────────────
const ethics = ref(false)
const copyright = ref(false)
const step4Errors = reactive({ ethics: '', copyright: '' })
const submitting = ref(false)
const submitError = ref('')
const successId = ref<string | null>(null)

function validateStep4(): boolean {
  step4Errors.ethics = ''
  step4Errors.copyright = ''
  let ok = true
  if (!ethics.value) { step4Errors.ethics = t('author.submit.validation.ethics_required'); ok = false }
  if (!copyright.value) { step4Errors.copyright = t('author.submit.validation.copyright_required'); ok = false }
  return ok
}

function previewTitle(): string {
  const t = step1.title
  return t.en || t.ru || t.uz || ''
}

function previewAbstract(): string {
  const a = step1.abstract
  const text = a.en || a.ru || a.uz || ''
  return text.slice(0, 200) + (text.length > 200 ? '...' : '')
}

async function submitArticle() {
  if (!validateStep4()) return
  submitting.value = true
  submitError.value = ''
  try {
    const payload = {
      title: step1.title,
      abstract: step1.abstract,
      keywords: step1.keywords,
      language: step1.language,
      category_id: step1.category_id || null,
      pdf_file_path: step3.pdfKey,
      pdf_file_size: step3.pdfSize,
      cover_letter: step3.coverLetter || null,
      co_authors: authors.value
        .filter((a) => !a.readonly)
        .map((a, idx) => ({
          user_id: a.user_id ?? null,
          guest_name: a.user_id ? null : a.name,
          guest_email: a.email ?? null,
          guest_affiliation: a.affiliation ?? null,
          guest_orcid: a.orcid ?? null,
          order: idx + 2,
          is_corresponding: a.is_corresponding,
        })),
    }
    const result = await api.post<{ id: string }>('/api/articles', payload)
    successId.value = result.id
    clearDraft()
  } catch (e: any) {
    submitError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    submitting.value = false
  }
}

// ─── Navigation ──────────────────────────────────────────────────────
function goNext() {
  if (currentStep.value === 0 && !validateStep1()) return
  if (currentStep.value === 2 && !validateStep3()) return
  currentStep.value++
}

function goPrev() {
  if (currentStep.value > 0) currentStep.value--
}
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <!-- Draft restore banner -->
    <div
      v-if="showRestoreBanner"
      class="border-b border-amber-200 bg-amber-50 px-4 py-3 dark:border-amber-900/50 dark:bg-amber-950/20"
    >
      <div class="mx-auto flex max-w-3xl items-center justify-between gap-3">
        <p class="text-sm text-amber-800 dark:text-amber-400">{{ t('author.submit.wizard.draft_restore_prompt') }}</p>
        <div class="flex gap-2 shrink-0">
          <button class="btn-ghost py-1 text-xs" @click="restoreDraft">{{ t('author.submit.wizard.restore') }}</button>
          <button class="text-xs text-slate-400 hover:text-slate-600" @click="clearDraft">{{ t('common.cancel') }}</button>
        </div>
      </div>
    </div>

    <!-- Header -->
    <div class="border-b border-slate-200 bg-slate-50 py-6 dark:border-slate-800 dark:bg-slate-900">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('submit.title') }}</h1>
      </div>
    </div>

    <!-- Progress bar -->
    <div class="border-b border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <div class="flex">
          <button
            v-for="(step, i) in STEPS"
            :key="step"
            class="flex flex-1 items-center justify-center gap-2 border-b-2 py-4 text-sm font-medium transition-colors"
            :class="[
              i === currentStep ? 'border-primary-600 text-primary-700 dark:text-primary-400' :
              i < currentStep ? 'border-primary-200 text-slate-500 dark:border-primary-900' :
              'border-transparent text-slate-400',
            ]"
            @click="i < currentStep ? currentStep = i : undefined"
          >
            <CheckCircle v-if="i < currentStep" :size="16" class="text-primary-600 dark:text-primary-400 hidden sm:block" />
            <span class="sm:hidden">{{ i + 1 }}</span>
            <span class="hidden sm:inline">{{ t(`author.submit.step${i + 1}_label`) }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Success state -->
    <div v-if="successId" class="flex flex-col items-center justify-center py-24 text-center px-4">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-950">
        <CheckCircle :size="32" class="text-green-500" />
      </div>
      <h2 class="mt-5 font-serif text-2xl font-bold text-slate-900 dark:text-white">
        {{ t('author.submit.success_title') }}
      </h2>
      <p class="mt-2 text-slate-500 dark:text-slate-400">{{ t('author.submit.success_desc') }}</p>
      <p class="mt-1 text-xs text-slate-400">ID: {{ successId }}</p>
      <div class="mt-8 flex gap-3">
        <router-link :to="{ name: 'article-status', params: { id: successId } }" class="btn-primary">
          {{ t('author.submit.track_submission') }}
        </router-link>
        <router-link :to="{ name: 'my-articles' }" class="btn-ghost">
          {{ t('author.myArticles.title') }}
        </router-link>
      </div>
    </div>

    <!-- Wizard steps -->
    <div v-else class="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">

      <!-- ── Step 1: Article Info ── -->
      <div v-if="currentStep === 0" class="space-y-6">
        <!-- Title tabs -->
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('submit.title_label') }} *
          </label>
          <div class="mb-2 flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-800 w-fit">
            <button
              v-for="lang in ['uz', 'ru', 'en'] as const"
              :key="lang"
              type="button"
              class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
              :class="titleTab === lang ? 'bg-white shadow text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'"
              @click="titleTab = lang"
            >
              {{ lang.toUpperCase() }}
            </button>
          </div>
          <textarea
            v-model="step1.title[titleTab]"
            rows="2"
            class="input-base resize-none"
            :placeholder="t('author.submit.title_placeholder')"
            :class="{ 'border-red-400': step1Errors.title }"
          />
          <p v-if="step1Errors.title" class="mt-1 flex items-center gap-1 text-xs text-red-500">
            <AlertCircle :size="12" />{{ step1Errors.title }}
          </p>
        </div>

        <!-- Abstract tabs -->
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('submit.abstract_label') }} *
          </label>
          <div class="mb-2 flex gap-1 rounded-lg bg-slate-100 p-1 dark:bg-slate-800 w-fit">
            <button
              v-for="lang in ['uz', 'ru', 'en'] as const"
              :key="lang"
              type="button"
              class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
              :class="abstractTab === lang ? 'bg-white shadow text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'"
              @click="abstractTab = lang"
            >
              {{ lang.toUpperCase() }}
            </button>
          </div>
          <textarea
            v-model="step1.abstract[abstractTab]"
            rows="5"
            class="input-base resize-none"
            :placeholder="t('author.submit.abstract_placeholder')"
            :class="{ 'border-red-400': step1Errors.abstract }"
          />
          <p v-if="step1Errors.abstract" class="mt-1 flex items-center gap-1 text-xs text-red-500">
            <AlertCircle :size="12" />{{ step1Errors.abstract }}
          </p>
        </div>

        <!-- Keywords -->
        <div>
          <label class="mb-2 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('submit.keywords_label') }} * <span class="font-normal text-slate-400">({{ t('author.submit.keywords_hint') }})</span>
          </label>
          <div
            class="flex min-h-[44px] flex-wrap items-center gap-2 rounded-xl border border-slate-300 bg-white p-2 focus-within:border-primary-500 focus-within:ring-1 focus-within:ring-primary-500 dark:border-slate-700 dark:bg-slate-900"
            :class="{ 'border-red-400': step1Errors.keywords }"
          >
            <span
              v-for="kw in step1.keywords"
              :key="kw"
              class="flex items-center gap-1 rounded-full bg-primary-100 px-2.5 py-0.5 text-xs font-medium text-primary-700 dark:bg-primary-950 dark:text-primary-300"
            >
              <Tag :size="10" />{{ kw }}
              <button type="button" @click="removeKeyword(kw)"><X :size="11" /></button>
            </span>
            <input
              v-model="step1.keywordInput"
              type="text"
              class="min-w-[120px] flex-1 border-none bg-transparent text-sm outline-none placeholder:text-slate-400 dark:text-white"
              :placeholder="step1.keywords.length === 0 ? t('author.submit.keywords_placeholder') : ''"
              @keydown="onKeywordKeydown"
              @blur="addKeyword"
            />
          </div>
          <p v-if="step1Errors.keywords" class="mt-1 flex items-center gap-1 text-xs text-red-500">
            <AlertCircle :size="12" />{{ step1Errors.keywords }}
          </p>
        </div>

        <!-- Language + Category row -->
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">
              {{ t('submit.language_label') }}
            </label>
            <select v-model="step1.language" class="input-base">
              <option value="uz">O'zbek</option>
              <option value="ru">Русский</option>
              <option value="en">English</option>
            </select>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">
              {{ t('submit.category_label') }}
            </label>
            <select v-model="step1.category_id" class="input-base" :disabled="categoriesLoading">
              <option value="">{{ t('common.all') }}</option>
              <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                {{ cat['name_' + step1.language as keyof typeof cat] ?? cat.name_en }}
              </option>
            </select>
          </div>
        </div>
      </div>

      <!-- ── Step 2: Authors ── -->
      <div v-else-if="currentStep === 1" class="space-y-4">
        <p class="text-sm text-slate-500 dark:text-slate-400">{{ t('author.submit.authors_hint') }}</p>

        <div class="space-y-2">
          <AuthorRow
            v-for="(author, idx) in authors"
            :key="author.id"
            :author="author"
            :index="idx"
            :can-remove="!author.readonly"
            @remove="removeAuthor"
            @toggle-corresponding="toggleCorresponding"
          />
        </div>

        <button
          type="button"
          class="btn-ghost w-full"
          @click="showCoAuthorModal = true"
        >
          <Plus :size="16" />{{ t('author.submit.add_coauthor') }}
        </button>
      </div>

      <!-- ── Step 3: PDF Upload ── -->
      <div v-else-if="currentStep === 2" class="space-y-6">
        <PdfUploadZone
          v-model="step3.pdfKey"
          v-model:file-name="step3.pdfName"
          v-model:file-size="step3.pdfSize"
        />
        <p v-if="step3Errors.pdf" class="flex items-center gap-1.5 text-sm text-red-500">
          <AlertCircle :size="15" />{{ step3Errors.pdf }}
        </p>

        <!-- Cover letter -->
        <div>
          <label class="mb-1.5 block text-sm font-semibold text-slate-700 dark:text-slate-300">
            {{ t('author.submit.cover_letter') }} <span class="font-normal text-slate-400">({{ t('common.all').replace('All', 'Optional') }})</span>
          </label>
          <textarea
            v-model="step3.coverLetter"
            rows="5"
            class="input-base resize-none"
            :placeholder="t('author.submit.cover_letter_placeholder')"
          />
        </div>
      </div>

      <!-- ── Step 4: Review & Submit ── -->
      <div v-else-if="currentStep === 3" class="space-y-6">
        <!-- Summary card -->
        <div class="card divide-y divide-slate-100 dark:divide-slate-800 overflow-hidden">
          <div class="p-5">
            <p class="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('submit.title_label') }}</p>
            <p class="font-medium text-slate-900 dark:text-white">{{ previewTitle() || '—' }}</p>
          </div>
          <div class="p-5">
            <p class="mb-1 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('submit.abstract_label') }}</p>
            <p class="text-sm text-slate-600 dark:text-slate-400">{{ previewAbstract() || '—' }}</p>
          </div>
          <div class="p-5">
            <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('article.authors') }}</p>
            <p class="text-sm text-slate-700 dark:text-slate-300">{{ authors.map((a) => a.name).join(', ') }}</p>
          </div>
          <div class="p-5">
            <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('article.keywords') }}</p>
            <div class="flex flex-wrap gap-1.5">
              <span
                v-for="kw in step1.keywords"
                :key="kw"
                class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-400"
              >{{ kw }}</span>
            </div>
          </div>
          <div class="flex gap-6 p-5">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('submit.language_label') }}</p>
              <p class="mt-0.5 text-sm text-slate-700 dark:text-slate-300">{{ step1.language.toUpperCase() }}</p>
            </div>
            <div>
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('upload.uploadSuccess') }}</p>
              <p class="mt-0.5 text-sm text-slate-700 dark:text-slate-300">{{ step3.pdfName || '—' }}</p>
            </div>
          </div>
        </div>

        <!-- Declarations -->
        <div class="space-y-3">
          <label class="flex cursor-pointer items-start gap-3">
            <input
              v-model="ethics"
              type="checkbox"
              class="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('author.submit.ethics_declaration') }}</span>
          </label>
          <p v-if="step4Errors.ethics" class="ml-7 text-xs text-red-500">{{ step4Errors.ethics }}</p>

          <label class="flex cursor-pointer items-start gap-3">
            <input
              v-model="copyright"
              type="checkbox"
              class="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm text-slate-700 dark:text-slate-300">{{ t('author.submit.copyright_agreement') }}</span>
          </label>
          <p v-if="step4Errors.copyright" class="ml-7 text-xs text-red-500">{{ step4Errors.copyright }}</p>
        </div>

        <!-- Submit error -->
        <div v-if="submitError" class="flex items-center gap-2 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/20 dark:text-red-400">
          <AlertCircle :size="16" />{{ submitError }}
        </div>
      </div>

      <!-- Nav buttons -->
      <div class="mt-8 flex items-center justify-between border-t border-slate-200 pt-6 dark:border-slate-800">
        <button
          v-if="currentStep > 0"
          type="button"
          class="btn-ghost"
          @click="goPrev"
        >
          <ChevronLeft :size="16" />{{ t('submit.prev') }}
        </button>
        <div v-else />

        <div class="flex items-center gap-3">
          <button type="button" class="btn-ghost text-sm" @click="saveDraft">
            <Save :size="15" />{{ t('submit.save_draft') }}
          </button>

          <button
            v-if="currentStep < 3"
            type="button"
            class="btn-primary"
            @click="goNext"
          >
            {{ t('submit.next') }}<ChevronRight :size="16" />
          </button>

          <button
            v-else
            type="button"
            class="btn-primary px-6"
            :disabled="submitting"
            @click="submitArticle"
          >
            <Send :size="16" :class="{ 'animate-pulse': submitting }" />
            {{ submitting ? t('contact.sending') : t('submit.submit_btn') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Co-author modal -->
    <CoAuthorModal
      v-if="showCoAuthorModal"
      @close="showCoAuthorModal = false"
      @add="addCoAuthor"
    />
  </div>
</template>
