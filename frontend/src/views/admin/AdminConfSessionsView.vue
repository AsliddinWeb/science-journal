<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()
const localeStore = useLocaleStore()

interface Session {
  id: string; conference_id: string
  title: Record<string, string>; description?: Record<string, string>
  order: number; date?: string | null; paper_count?: number
}
interface Conference {
  id: string; title: Record<string, string>; year: number
  sessions: Session[]
}

const conferences = ref<Conference[]>([])
const selectedConfId = ref<string>('')
const loading = ref(true)

const showForm = ref(false)
const editing = ref<Session | null>(null)
const saving = ref(false)
const langTab = ref<'uz' | 'ru' | 'en'>('uz')

const form = reactive({
  title: { uz: '', ru: '', en: '' } as Record<string, string>,
  description: { uz: '', ru: '', en: '' } as Record<string, string>,
  order: 1,
  date: '' as string,
})

const showDelete = ref(false)
const deleteTarget = ref<Session | null>(null)
const deleting = ref(false)

const currentConf = computed(() => conferences.value.find(c => c.id === selectedConfId.value) || null)
const sessions = computed<Session[]>(() =>
  [...(currentConf.value?.sessions || [])].sort((a, b) => a.order - b.order)
)

async function load() {
  loading.value = true
  try {
    const data = await api.get<{ items: Conference[] }>('/api/admin/conferences?limit=100')
    conferences.value = data.items
    if (!selectedConfId.value && data.items.length) selectedConfId.value = data.items[0].id
  } catch {} finally { loading.value = false }
}

function openCreate() {
  editing.value = null
  form.title = { uz: '', ru: '', en: '' }
  form.description = { uz: '', ru: '', en: '' }
  form.order = (sessions.value.length || 0) + 1
  form.date = ''
  langTab.value = 'uz'
  showForm.value = true
}

function openEdit(s: Session) {
  editing.value = s
  form.title = { uz: s.title?.uz || '', ru: s.title?.ru || '', en: s.title?.en || '' }
  form.description = {
    uz: s.description?.uz || '', ru: s.description?.ru || '', en: s.description?.en || ''
  }
  form.order = s.order || 1
  form.date = s.date ? String(s.date).split('T')[0] : ''
  langTab.value = 'uz'
  showForm.value = true
}

async function save() {
  if (!selectedConfId.value) return
  if (!form.title.uz && !form.title.ru && !form.title.en) {
    toast.error('Sarlavha kiritilmagan'); return
  }
  saving.value = true
  try {
    const payload = {
      title: form.title,
      description: form.description,
      order: form.order,
      date: form.date || null,
    }
    if (editing.value) {
      await api.put(`/api/admin/conferences/${selectedConfId.value}/sessions/${editing.value.id}`, payload)
      toast.success(t('admin.conferences.session_updated'))
    } else {
      await api.post(`/api/admin/conferences/${selectedConfId.value}/sessions`, payload)
      toast.success(t('admin.conferences.session_created'))
    }
    showForm.value = false
    await load()
  } catch (e: any) {
    toast.error(e?.response?.data?.detail || 'Xatolik')
  } finally { saving.value = false }
}

function confirmDelete(s: Session) { deleteTarget.value = s; showDelete.value = true }
async function doDelete() {
  if (!deleteTarget.value) return
  deleting.value = true
  try {
    await api.delete(`/api/admin/conferences/${deleteTarget.value.conference_id}/sessions/${deleteTarget.value.id}`)
    toast.success(t('admin.conferences.session_deleted'))
    showDelete.value = false
    await load()
  } catch { toast.error('Xatolik') }
  finally { deleting.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.conferences.sessions') }}</h1>
      <button
        class="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        :disabled="!selectedConfId"
        @click="openCreate">
        <Plus :size="15" />{{ t('admin.conferences.add_session') }}
      </button>
    </div>

    <div class="mb-4 flex flex-wrap gap-3">
      <select v-model="selectedConfId" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200">
        <option value="" disabled>{{ t('admin.sidebar.conferences') }}</option>
        <option v-for="c in conferences" :key="c.id" :value="c.id">
          {{ getLocalizedField(c.title, localeStore.current, '') }} ({{ c.year }})
        </option>
      </select>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
      <div v-else-if="!conferences.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>
      <div v-else-if="!sessions.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-5 py-3 w-16">#</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_title') }}</th>
              <th class="px-4 py-3">{{ t('admin.conferences.date') }}</th>
              <th class="px-4 py-3">{{ t('admin.conferences.papers') }}</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in sessions" :key="s.id" class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50">
              <td class="px-5 py-3 text-slate-500">{{ s.order }}</td>
              <td class="px-4 py-3 font-medium text-slate-800 dark:text-slate-200">
                {{ getLocalizedField(s.title, localeStore.current, '') }}
              </td>
              <td class="px-4 py-3 text-slate-500">{{ s.date || '—' }}</td>
              <td class="px-4 py-3 text-slate-500">{{ s.paper_count ?? 0 }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <button class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30" @click="openEdit(s)"><Pencil :size="14" /></button>
                  <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(s)"><Trash2 :size="14" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit modal -->
    <div v-if="showForm" class="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/50 p-4" @click.self="showForm = false">
      <div class="w-full max-w-xl rounded-xl bg-white p-6 shadow-xl dark:bg-slate-800">
        <div class="mb-4 flex items-center justify-between">
          <h3 class="font-serif text-lg font-bold text-slate-900 dark:text-white">
            {{ editing ? t('admin.conferences.edit_session') : t('admin.conferences.add_session') }}
          </h3>
          <button class="text-slate-400 hover:text-slate-600" @click="showForm = false"><X :size="18" /></button>
        </div>

        <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
          <button v-for="l in (['uz', 'ru', 'en'] as const)" :key="l"
                  class="rounded-md px-4 py-1.5 text-sm font-medium transition"
                  :class="langTab === l ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'"
                  @click="langTab = l">{{ l.toUpperCase() }}</button>
        </div>

        <div class="mb-3">
          <label class="label-base">{{ t('admin.articles.col_title') }} ({{ langTab.toUpperCase() }})</label>
          <input v-model="form.title[langTab]" class="input-base w-full" />
        </div>
        <div class="mb-3">
          <label class="label-base">{{ t('article.abstract') }} ({{ langTab.toUpperCase() }})</label>
          <textarea v-model="form.description[langTab]" rows="3" class="input-base w-full resize-none" />
        </div>
        <div class="mb-4 grid grid-cols-2 gap-3">
          <div>
            <label class="label-base">Tartib</label>
            <input v-model.number="form.order" type="number" class="input-base w-full" />
          </div>
          <div>
            <label class="label-base">{{ t('admin.conferences.date') }}</label>
            <input v-model="form.date" type="date" class="input-base w-full" />
          </div>
        </div>
        <div class="flex justify-end gap-2">
          <AppButton variant="secondary" @click="showForm = false">{{ t('common.cancel') }}</AppButton>
          <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
        </div>
      </div>
    </div>

    <ConfirmModal v-if="showDelete"
                  :title="t('common.delete')"
                  :message="t('common.delete_confirm_text')"
                  :loading="deleting" danger
                  @confirm="doDelete" @cancel="showDelete = false" />
  </div>
</template>
