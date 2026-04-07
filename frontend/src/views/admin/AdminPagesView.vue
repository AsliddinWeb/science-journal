<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import {
  PenLine, Eye, ArrowLeft, Bold, Italic, Heading1, Heading2, Heading3,
  Link2, List, ListOrdered, Quote, Code, Image as ImageIcon, Minus, Undo, Redo, Loader2,
} from 'lucide-vue-next'
import { marked } from 'marked'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { formatDateShort } from '@/utils/formatDate'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'

const { t } = useI18n()
const toast = useToast()

interface Page {
  id: string
  slug: string
  title_uz: string
  title_ru: string
  title_en: string
  content_uz?: string
  content_ru?: string
  content_en?: string
  is_published: boolean
  updated_at: string
}

const pages = ref<Page[]>([])
const loading = ref(true)
const editingPage = ref<Page | null>(null)
const activeTab = ref<'uz' | 'ru' | 'en'>('uz')
const previewMode = ref(false)
const saving = ref(false)
const toggling = ref<string | null>(null)
const creating = ref(false)
const newSlug = ref('')

const form = ref({
  title_uz: '', title_ru: '', title_en: '',
  content_uz: '', content_ru: '', content_en: '',
  is_published: false,
})

onMounted(async () => {
  try {
    // Get all pages (including unpublished)
    const data = await api.get<Page[]>('/api/pages')
    pages.value = data
  } catch {
    pages.value = []
  } finally {
    loading.value = false
  }
})

async function createPage() {
  if (!newSlug.value.trim()) return
  saving.value = true
  try {
    const created = await api.post<Page>('/api/pages', {
      slug: newSlug.value.trim(),
      title_uz: newSlug.value,
      title_ru: newSlug.value,
      title_en: newSlug.value,
      is_published: false,
    })
    pages.value.push(created)
    creating.value = false
    newSlug.value = ''
    startEdit(created)
  } catch { toast.error("Slug allaqachon mavjud yoki xatolik") }
  finally { saving.value = false }
}

function startEdit(page: Page) {
  editingPage.value = page
  Object.assign(form.value, {
    title_uz: page.title_uz,
    title_ru: page.title_ru,
    title_en: page.title_en,
    content_uz: page.content_uz || '',
    content_ru: page.content_ru || '',
    content_en: page.content_en || '',
    is_published: page.is_published,
  })
  previewMode.value = false
  activeTab.value = 'uz'
}

function cancelEdit() {
  editingPage.value = null
}

async function savePage(publish?: boolean) {
  if (!editingPage.value) return
  saving.value = true
  if (publish !== undefined) form.value.is_published = publish
  try {
    const updated = await api.put<Page>(`/api/pages/${editingPage.value.slug}`, { ...form.value, slug: editingPage.value.slug })
    const idx = pages.value.findIndex((p) => p.id === editingPage.value!.id)
    if (idx !== -1) pages.value[idx] = updated
    editingPage.value = updated
    toast.success(publish ? t('admin.pages.publish') + ' muvaffaqiyatli' : t('admin.pages.saved'))
  } catch { toast.error('Saqlashda xatolik') }
  finally { saving.value = false }
}

async function togglePublish(page: Page) {
  toggling.value = page.id
  try {
    const updated = await api.put<Page>(`/api/pages/${page.slug}`, {
      ...page,
      is_published: !page.is_published,
    })
    const idx = pages.value.findIndex((p) => p.id === page.id)
    if (idx !== -1) pages.value[idx] = updated
  } catch { toast.error('Xatolik') }
  finally { toggling.value = null }
}

const currentContent = computed({
  get() {
    return (form.value as any)[`content_${activeTab.value}`] as string
  },
  set(val: string) {
    ;(form.value as any)[`content_${activeTab.value}`] = val
  },
})

const currentTitle = computed({
  get() { return (form.value as any)[`title_${activeTab.value}`] as string },
  set(val: string) { ;(form.value as any)[`title_${activeTab.value}`] = val },
})

marked.setOptions({ breaks: true, gfm: true })

const previewHtml = computed(() => {
  try { return marked.parse(currentContent.value || '') as string } catch { return '' }
})

type Toolbar = 'bold' | 'italic' | 'h1' | 'h2' | 'h3' | 'link' | 'list' | 'ol' | 'quote' | 'code' | 'hr' | 'image'

function insertMarkdown(type: Toolbar) {
  const textarea = document.querySelector<HTMLTextAreaElement>('#content-editor')
  if (!textarea) return
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const sel = textarea.value.slice(start, end)
  const before = textarea.value.slice(0, start)
  const after = textarea.value.slice(end)

  const wrap = (prefix: string, suffix: string, placeholder: string) => {
    const text = sel || placeholder
    currentContent.value = before + prefix + text + suffix + after
    setTimeout(() => {
      textarea.focus()
      const cursor = start + prefix.length + text.length
      textarea.setSelectionRange(cursor, cursor)
    }, 0)
  }

  const line = (prefix: string, placeholder: string) => {
    const needsNewline = before.length > 0 && !before.endsWith('\n')
    const text = sel || placeholder
    currentContent.value = before + (needsNewline ? '\n' : '') + prefix + text + '\n' + after
    setTimeout(() => {
      textarea.focus()
      const cursor = start + (needsNewline ? 1 : 0) + prefix.length + text.length
      textarea.setSelectionRange(cursor, cursor)
    }, 0)
  }

  switch (type) {
    case 'bold': return wrap('**', '**', 'qalin matn')
    case 'italic': return wrap('*', '*', 'kursiv matn')
    case 'h1': return line('# ', 'Asosiy sarlavha')
    case 'h2': return line('## ', 'Bo\'lim sarlavhasi')
    case 'h3': return line('### ', 'Kichik sarlavha')
    case 'link': return wrap('[', '](https://)', 'havola matni')
    case 'image': return wrap('![', '](https://rasm.png)', 'alt matn')
    case 'list': return line('- ', 'ro\'yxat elementi')
    case 'ol': return line('1. ', 'raqamli element')
    case 'quote': return line('> ', 'iqtibos matni')
    case 'code': return wrap('`', '`', 'kod')
    case 'hr':
      currentContent.value = before + (before.endsWith('\n') ? '' : '\n') + '\n---\n\n' + after
      return
  }
}

// Image upload
const uploadingImg = ref(false)
async function uploadEditorImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingImg.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ url: string; s3_key: string }>('/api/upload/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const url = res.url || `/api/uploads/${res.s3_key}`
    const textarea = document.querySelector<HTMLTextAreaElement>('#content-editor')
    const insertion = `\n![Rasm](${url})\n`
    if (textarea) {
      const pos = textarea.selectionStart
      currentContent.value = textarea.value.slice(0, pos) + insertion + textarea.value.slice(pos)
    } else {
      currentContent.value += insertion
    }
    toast.success('Rasm yuklandi')
  } catch {
    toast.error('Rasm yuklanmadi')
  } finally {
    uploadingImg.value = false
    ;(e.target as HTMLInputElement).value = ''
  }
}
</script>

<template>
  <div>
    <!-- List view -->
    <template v-if="!editingPage">
      <div class="mb-6 flex items-center justify-between">
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.pages.title') }}</h1>
        <AppButton @click="creating = true">+ {{ t('admin.pages.create') }}</AppButton>
      </div>

      <!-- Create modal -->
      <Teleport to="body">
        <div v-if="creating" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800">
            <h2 class="mb-4 text-base font-semibold text-slate-900 dark:text-white">{{ t('admin.pages.create') }}</h2>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">Slug</label>
            <input
              v-model="newSlug"
              class="input-base mb-1 w-full font-mono text-sm"
              placeholder="masalan: about, author-guidelines"
              @keyup.enter="createPage"
            />
            <p class="mb-5 text-xs text-slate-400">/pages/<strong>{{ newSlug || 'slug' }}</strong></p>
            <div class="flex justify-end gap-2">
              <AppButton variant="secondary" @click="creating = false; newSlug = ''">{{ t('common.cancel') }}</AppButton>
              <AppButton :loading="saving" @click="createPage">{{ t('common.create') }}</AppButton>
            </div>
          </div>
        </div>
      </Teleport>

      <div v-if="loading" class="flex justify-center py-16">
        <AppSpinner :size="32" class="text-primary-500" />
      </div>
      <div v-else-if="!pages.length" class="rounded-xl border border-slate-200 bg-white p-8 text-center text-slate-400 dark:border-slate-700 dark:bg-slate-800">
        {{ t('common.no_data') }}
      </div>
      <div v-else class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-5 py-3">{{ t('admin.pages.slug') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_title') }}</th>
              <th class="px-4 py-3">{{ t('admin.pages.updated') }}</th>
              <th class="px-4 py-3">{{ t('common.active') }}</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="page in pages"
              :key="page.id"
              class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50"
            >
              <td class="px-5 py-3 font-mono text-xs text-slate-500">/{{ page.slug }}</td>
              <td class="px-4 py-3 font-medium text-slate-800 dark:text-slate-200">{{ page.title_en || page.title_uz }}</td>
              <td class="px-4 py-3 text-slate-500">{{ formatDateShort(page.updated_at) }}</td>
              <td class="px-4 py-3">
                <button
                  :disabled="toggling === page.id"
                  class="rounded-full px-2.5 py-1 text-xs font-medium transition"
                  :class="page.is_published ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-700'"
                  @click="togglePublish(page)"
                >
                  {{ page.is_published ? t('common.active') : t('common.inactive') }}
                </button>
              </td>
              <td class="px-4 py-3">
                <button
                  class="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-1.5 text-xs font-medium text-primary-700 hover:bg-primary-100 dark:bg-primary-950/50 dark:text-primary-300"
                  @click="startEdit(page)"
                >
                  <PenLine :size="13" />{{ t('common.edit') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Edit view -->
    <template v-else>
      <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <button
            class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
            @click="cancelEdit"
          >
            <ArrowLeft :size="16" />{{ t('common.back') }}
          </button>
          <span class="font-mono text-xs text-slate-400">/{{ editingPage.slug }}</span>
        </div>
        <div class="flex gap-2">
          <button
            class="rounded-lg border border-slate-200 px-3 py-2 text-sm transition hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700"
            :class="previewMode ? 'bg-slate-100 dark:bg-slate-700' : ''"
            @click="previewMode = !previewMode"
          >
            <Eye :size="15" class="inline mr-1" />{{ t('admin.pages.preview') }}
          </button>
          <AppButton variant="secondary" :loading="saving" @click="savePage(false)">{{ t('admin.pages.saveDraft') }}</AppButton>
          <AppButton :loading="saving" @click="savePage(true)">{{ t('admin.pages.publish') }}</AppButton>
        </div>
      </div>

      <!-- Lang tabs -->
      <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
        <button
          v-for="lang in ['uz', 'ru', 'en']"
          :key="lang"
          class="rounded-md px-4 py-1.5 text-sm font-medium transition"
          :class="activeTab === lang ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500 hover:text-slate-700'"
          @click="activeTab = lang as 'uz' | 'ru' | 'en'"
        >
          {{ lang.toUpperCase() }}
        </button>
      </div>

      <!-- Title -->
      <div class="mb-4">
        <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('admin.pages.titleLabel') }}</label>
        <input
          v-model="currentTitle"
          class="input-base w-full text-base"
          :placeholder="`Sarlavha (${activeTab})`"
        />
      </div>

      <!-- Toolbar -->
      <div v-if="!previewMode" class="flex flex-wrap items-center gap-0.5 rounded-t-lg border border-b-0 border-slate-200 bg-slate-50 px-2 py-1.5 dark:border-slate-700 dark:bg-slate-800">
        <!-- Headings -->
        <button type="button" title="Heading 1" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('h1')">
          <Heading1 :size="16" />
        </button>
        <button type="button" title="Heading 2" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('h2')">
          <Heading2 :size="16" />
        </button>
        <button type="button" title="Heading 3" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('h3')">
          <Heading3 :size="16" />
        </button>

        <div class="mx-1 h-5 w-px bg-slate-300 dark:bg-slate-600" />

        <!-- Inline formatting -->
        <button type="button" title="Bold (Ctrl+B)" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('bold')">
          <Bold :size="16" />
        </button>
        <button type="button" title="Italic (Ctrl+I)" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('italic')">
          <Italic :size="16" />
        </button>
        <button type="button" title="Inline code" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('code')">
          <Code :size="16" />
        </button>

        <div class="mx-1 h-5 w-px bg-slate-300 dark:bg-slate-600" />

        <!-- Lists -->
        <button type="button" title="Bullet list" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('list')">
          <List :size="16" />
        </button>
        <button type="button" title="Numbered list" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('ol')">
          <ListOrdered :size="16" />
        </button>
        <button type="button" title="Quote" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('quote')">
          <Quote :size="16" />
        </button>

        <div class="mx-1 h-5 w-px bg-slate-300 dark:bg-slate-600" />

        <!-- Link / image / hr -->
        <button type="button" title="Link" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('link')">
          <Link2 :size="16" />
        </button>
        <label title="Upload image" class="cursor-pointer rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700">
          <Loader2 v-if="uploadingImg" :size="16" class="animate-spin" />
          <ImageIcon v-else :size="16" />
          <input type="file" accept="image/*" class="hidden" @change="uploadEditorImage" />
        </label>
        <button type="button" title="Horizontal rule" class="rounded p-1.5 text-slate-600 hover:bg-white hover:text-primary-600 dark:text-slate-400 dark:hover:bg-slate-700" @click="insertMarkdown('hr')">
          <Minus :size="16" />
        </button>

        <div class="flex-1" />
        <span class="text-xs text-slate-400">{{ currentContent.length }} belgi</span>
      </div>

      <!-- Content editor or preview -->
      <div v-if="!previewMode">
        <textarea
          id="content-editor"
          v-model="currentContent"
          rows="22"
          class="w-full rounded-b-lg border border-slate-200 bg-white px-5 py-4 font-mono text-sm leading-relaxed text-slate-800 outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          :placeholder="`Kontentni markdown formatida yozing (${activeTab})...\n\n# Sarlavha\n## Bo'lim\nParagrafda **qalin** va *kursiv* matn.\n\n- ro'yxat\n- element\n\n[Havola](https://example.com)`"
        />
      </div>
      <div
        v-else
        class="prose prose-slate max-w-none rounded-lg border border-slate-200 bg-white p-8 dark:border-slate-700 dark:bg-slate-800 dark:prose-invert
          prose-headings:font-serif prose-headings:font-bold prose-headings:text-journal-800 dark:prose-headings:text-primary-300
          prose-h1:text-3xl prose-h1:border-b prose-h1:border-primary-200 prose-h1:pb-3 prose-h1:mb-6
          prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4
          prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3
          prose-p:text-slate-600 prose-p:leading-relaxed dark:prose-p:text-slate-300
          prose-a:text-primary-600 dark:prose-a:text-primary-400 prose-a:no-underline hover:prose-a:underline
          prose-strong:text-journal-800 dark:prose-strong:text-slate-100
          prose-blockquote:border-primary-400 prose-blockquote:bg-stone-50 dark:prose-blockquote:bg-slate-900
          prose-code:bg-stone-100 prose-code:text-primary-700 prose-code:rounded prose-code:px-1.5 prose-code:py-0.5 dark:prose-code:bg-slate-900
          prose-img:rounded-xl prose-img:shadow-md
          prose-hr:border-stone-200 dark:prose-hr:border-slate-700
          prose-ul:text-slate-600 dark:prose-ul:text-slate-300"
        v-html="previewHtml"
      />
    </template>
  </div>
</template>
