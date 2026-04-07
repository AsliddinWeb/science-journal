<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, X, Check, FileText, Calendar, MapPin } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'
import type { Conference, ConferenceSession } from '@/types/conference'

const { t } = useI18n()
const router = useRouter()
const toast = useToast()
const localeStore = useLocaleStore()

const conferences = ref<Conference[]>([])
const loading = ref(true)
const saving = ref(false)
const showDeleteModal = ref(false)
const deleteTargetId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

// Conference drawer
const drawer = ref(false)
const editingId = ref<string | null>(null)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const form = ref({
  title: { uz: '', ru: '', en: '' },
  description: { uz: '', ru: '', en: '' },
  location: '',
  start_date: '',
  end_date: '',
  year: new Date().getFullYear(),
  organizer: '',
  website_url: '',
  is_active: true,
  cover_image_url: '',
})

// Session drawer
const sessionDrawer = ref(false)
const sessionConfId = ref('')
const editingSessionId = ref<string | null>(null)
const sessionForm = ref({
  title: { uz: '', ru: '', en: '' },
  description: { uz: '', ru: '', en: '' },
  order: 1,
  date: '',
})

async function load() {
  loading.value = true
  try {
    const data = await api.get<{ items: Conference[] }>('/api/admin/conferences?limit=100')
    conferences.value = data.items
  } catch {
    conferences.value = []
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { title: { uz: '', ru: '', en: '' }, description: { uz: '', ru: '', en: '' }, location: '', start_date: '', end_date: '', year: new Date().getFullYear(), organizer: '', website_url: '', is_active: true, cover_image_url: '' }
  langTab.value = 'uz'
  drawer.value = true
}

function openEdit(conf: Conference) {
  editingId.value = conf.id
  form.value = {
    title: { uz: conf.title.uz || '', ru: conf.title.ru || '', en: conf.title.en || '' },
    description: { uz: conf.description?.uz || '', ru: conf.description?.ru || '', en: conf.description?.en || '' },
    location: conf.location || '',
    start_date: conf.start_date || '',
    end_date: conf.end_date || '',
    year: conf.year,
    organizer: conf.organizer || '',
    website_url: conf.website_url || '',
    is_active: conf.is_active,
    cover_image_url: conf.cover_image_url || '',
  }
  langTab.value = 'uz'
  drawer.value = true
}

async function save() {
  if (!form.value.title.uz && !form.value.title.ru && !form.value.title.en) {
    toast.error("Sarlavha kiriting"); return
  }
  saving.value = true
  try {
    const payload = { ...form.value, cover_image_url: form.value.cover_image_url || null }
    if (editingId.value) {
      const updated = await api.put<Conference>(`/api/admin/conferences/${editingId.value}`, payload)
      const idx = conferences.value.findIndex(c => c.id === editingId.value)
      if (idx !== -1) conferences.value[idx] = updated
      toast.success(t('admin.conferences.updated'))
    } else {
      const created = await api.post<Conference>('/api/admin/conferences', payload)
      conferences.value.unshift(created)
      toast.success(t('admin.conferences.created'))
    }
    drawer.value = false
  } catch { toast.error("Xatolik") }
  finally { saving.value = false }
}

function confirmDelete(id: string) { deleteTargetId.value = id; showDeleteModal.value = true }

async function doDelete() {
  if (!deleteTargetId.value) return
  deletingId.value = deleteTargetId.value
  try {
    await api.delete(`/api/admin/conferences/${deleteTargetId.value}`)
    conferences.value = conferences.value.filter(c => c.id !== deleteTargetId.value)
    toast.success(t('admin.conferences.deleted'))
    showDeleteModal.value = false
  } catch { toast.error("Xatolik") }
  finally { deletingId.value = null }
}

// Sessions
function openAddSession(confId: string) {
  sessionConfId.value = confId
  editingSessionId.value = null
  sessionForm.value = { title: { uz: '', ru: '', en: '' }, description: { uz: '', ru: '', en: '' }, order: 1, date: '' }
  langTab.value = 'uz'
  sessionDrawer.value = true
}

function openEditSession(confId: string, sess: ConferenceSession) {
  sessionConfId.value = confId
  editingSessionId.value = sess.id
  sessionForm.value = {
    title: { uz: sess.title.uz || '', ru: sess.title.ru || '', en: sess.title.en || '' },
    description: { uz: sess.description?.uz || '', ru: sess.description?.ru || '', en: sess.description?.en || '' },
    order: sess.order,
    date: sess.date || '',
  }
  langTab.value = 'uz'
  sessionDrawer.value = true
}

async function saveSession() {
  saving.value = true
  try {
    if (editingSessionId.value) {
      await api.put(`/api/admin/conferences/${sessionConfId.value}/sessions/${editingSessionId.value}`, sessionForm.value)
      toast.success(t('admin.conferences.session_updated'))
    } else {
      await api.post(`/api/admin/conferences/${sessionConfId.value}/sessions`, sessionForm.value)
      toast.success(t('admin.conferences.session_created'))
    }
    sessionDrawer.value = false
    await load()
  } catch { toast.error("Xatolik") }
  finally { saving.value = false }
}

async function deleteSession(confId: string, sessionId: string) {
  try {
    await api.delete(`/api/admin/conferences/${confId}/sessions/${sessionId}`)
    toast.success(t('admin.conferences.session_deleted'))
    await load()
  } catch { toast.error("Xatolik") }
}

// Image upload
const uploading = ref(false)
async function uploadImage(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string }>('/api/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
    form.value.cover_image_url = res.s3_key
  } catch { toast.error("Rasm yuklanmadi") }
  finally { uploading.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.conferences.title') }}</h1>
      <AppButton @click="openCreate"><Plus :size="15" class="mr-1" />{{ t('admin.conferences.create') }}</AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
    <div v-else-if="!conferences.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>

    <div v-else class="space-y-4">
      <div v-for="conf in conferences" :key="conf.id" class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
        <div class="flex items-start justify-between gap-4 p-5">
          <div class="flex-1 min-w-0">
            <h3 class="font-serif text-lg font-bold text-slate-900 dark:text-white">
              {{ getLocalizedField(conf.title, localeStore.current, '') }}
            </h3>
            <div class="mt-2 flex flex-wrap gap-3 text-sm text-slate-500">
              <span v-if="conf.location" class="flex items-center gap-1"><MapPin :size="13" />{{ conf.location }}</span>
              <span v-if="conf.start_date" class="flex items-center gap-1"><Calendar :size="13" />{{ conf.start_date }}</span>
              <span class="font-medium">{{ conf.year }}</span>
            </div>
          </div>
          <div class="flex items-center gap-1">
            <button class="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-primary-600 dark:hover:bg-slate-700" @click="router.push(`/admin/conferences/${conf.id}/papers`)">
              <FileText :size="15" />
            </button>
            <button class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30" @click="openEdit(conf)">
              <Pencil :size="15" />
            </button>
            <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(conf.id)">
              <Trash2 :size="15" />
            </button>
          </div>
        </div>

        <!-- Sessions -->
        <div v-if="conf.sessions?.length" class="border-t border-slate-100 px-5 py-3 dark:border-slate-700">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ t('admin.conferences.sessions') }}</span>
            <button class="text-xs font-medium text-primary-600 hover:underline" @click="openAddSession(conf.id)">+ {{ t('admin.conferences.add_session') }}</button>
          </div>
          <div class="space-y-1">
            <div v-for="sess in conf.sessions" :key="sess.id" class="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-700/50">
              <span class="text-sm text-slate-700 dark:text-slate-300">{{ getLocalizedField(sess.title, localeStore.current, '') }}</span>
              <div class="flex items-center gap-1">
                <button class="rounded p-1 text-slate-400 hover:text-amber-600" @click="openEditSession(conf.id, sess)"><Pencil :size="12" /></button>
                <button class="rounded p-1 text-slate-400 hover:text-red-500" @click="deleteSession(conf.id, sess.id)"><Trash2 :size="12" /></button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="border-t border-slate-100 px-5 py-3 dark:border-slate-700">
          <button class="text-xs font-medium text-primary-600 hover:underline" @click="openAddSession(conf.id)">+ {{ t('admin.conferences.add_session') }}</button>
        </div>
      </div>
    </div>

    <!-- Conference Drawer -->
    <Teleport to="body">
      <Transition enter-active-class="transition-all duration-200" enter-from-class="opacity-0" leave-active-class="transition-all duration-150" leave-to-class="opacity-0">
        <div v-if="drawer" class="fixed inset-0 z-40 flex justify-end bg-black/40" @click.self="drawer = false">
          <div class="relative flex h-full w-full max-w-lg flex-col bg-white shadow-2xl dark:bg-slate-900">
            <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
              <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ editingId ? t('admin.conferences.edit') : t('admin.conferences.create') }}</h2>
              <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800" @click="drawer = false"><X :size="18" /></button>
            </div>
            <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
              <!-- Lang tabs -->
              <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
                <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="rounded-md px-3 py-1.5 text-sm font-medium transition" :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'" @click="langTab = l">{{ l.toUpperCase() }}</button>
              </div>

              <div>
                <label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }}) *</label>
                <input v-model="form.title[langTab]" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.pages.contentLabel') || 'Tavsif' }} ({{ langTab.toUpperCase() }})</label>
                <textarea v-model="form.description[langTab]" rows="3" class="input-base w-full resize-none" />
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div><label class="label-base">{{ t('admin.conferences.location') }}</label><input v-model="form.location" class="input-base w-full" /></div>
                <div><label class="label-base">{{ t('admin.conferences.organizer') }}</label><input v-model="form.organizer" class="input-base w-full" /></div>
              </div>
              <div class="grid grid-cols-3 gap-3">
                <div><label class="label-base">{{ t('admin.conferences.date') }}</label><input v-model="form.start_date" type="date" class="input-base w-full" /></div>
                <div><label class="label-base">Tugash</label><input v-model="form.end_date" type="date" class="input-base w-full" /></div>
                <div><label class="label-base">Yil</label><input v-model.number="form.year" type="number" class="input-base w-full" /></div>
              </div>
              <div><label class="label-base">Veb-sayt</label><input v-model="form.website_url" class="input-base w-full" placeholder="https://..." /></div>
              <div>
                <label class="label-base">{{ t('admin.conferences.cover_image') }}</label>
                <div v-if="form.cover_image_url" class="mb-2 rounded-lg overflow-hidden">
                  <img :src="`/api/uploads/${form.cover_image_url}`" class="h-32 w-full object-cover" />
                  <button class="mt-1 text-xs text-red-500 hover:underline" @click="form.cover_image_url = ''">{{ t('common.delete') }}</button>
                </div>
                <label class="flex cursor-pointer items-center gap-2 rounded-lg border-2 border-dashed border-slate-300 px-4 py-3 hover:border-primary-400 dark:border-slate-600">
                  <span class="text-sm text-slate-500">{{ uploading ? 'Yuklanmoqda...' : t('admin.conferences.cover_image_hint') }}</span>
                  <input type="file" accept="image/*" class="hidden" @change="uploadImage" />
                </label>
              </div>
              <label class="flex items-center gap-2 cursor-pointer text-sm text-slate-700 dark:text-slate-300">
                <input v-model="form.is_active" type="checkbox" class="h-4 w-4 rounded accent-primary-600" />
                {{ t('common.active') }}
              </label>
            </div>
            <div class="border-t border-slate-200 px-6 py-4 dark:border-slate-700 flex justify-end gap-2">
              <AppButton variant="secondary" @click="drawer = false">{{ t('common.cancel') }}</AppButton>
              <AppButton :loading="saving" @click="save"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Session Drawer -->
    <Teleport to="body">
      <Transition enter-active-class="transition-all duration-200" enter-from-class="opacity-0" leave-active-class="transition-all duration-150" leave-to-class="opacity-0">
        <div v-if="sessionDrawer" class="fixed inset-0 z-50 flex justify-end bg-black/40" @click.self="sessionDrawer = false">
          <div class="relative flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-slate-900">
            <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
              <h2 class="text-base font-semibold text-slate-900 dark:text-white">{{ editingSessionId ? t('admin.conferences.edit_session') : t('admin.conferences.add_session') }}</h2>
              <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800" @click="sessionDrawer = false"><X :size="18" /></button>
            </div>
            <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">
              <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
                <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l" class="rounded-md px-3 py-1.5 text-sm font-medium transition" :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'" @click="langTab = l">{{ l.toUpperCase() }}</button>
              </div>
              <div><label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label><input v-model="sessionForm.title[langTab]" class="input-base w-full" /></div>
              <div><label class="label-base">Tavsif ({{ langTab.toUpperCase() }})</label><textarea v-model="sessionForm.description[langTab]" rows="2" class="input-base w-full resize-none" /></div>
              <div class="grid grid-cols-2 gap-3">
                <div><label class="label-base">Tartib</label><input v-model.number="sessionForm.order" type="number" min="1" class="input-base w-full" /></div>
                <div><label class="label-base">Sana</label><input v-model="sessionForm.date" type="date" class="input-base w-full" /></div>
              </div>
            </div>
            <div class="border-t border-slate-200 px-6 py-4 dark:border-slate-700 flex justify-end gap-2">
              <AppButton variant="secondary" @click="sessionDrawer = false">{{ t('common.cancel') }}</AppButton>
              <AppButton :loading="saving" @click="saveSession"><Check :size="15" class="mr-1" />{{ t('common.save') }}</AppButton>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <ConfirmModal v-if="showDeleteModal" :title="t('admin.conferences.delete_confirm')" :message="t('common.delete_confirm_text')" :loading="!!deletingId" danger @confirm="doDelete" @cancel="showDeleteModal = false" />
  </div>
</template>
