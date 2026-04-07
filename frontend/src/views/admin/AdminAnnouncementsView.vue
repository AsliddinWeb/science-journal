<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { formatDateShort } from '@/utils/formatDate'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()

interface Announcement {
  id: string
  title_uz: string
  title_ru: string
  title_en: string
  content_uz?: string
  content_ru?: string
  content_en?: string
  is_active: boolean
  published_at?: string
  expires_at?: string
  created_at: string
}

const announcements = ref<Announcement[]>([])
const loading = ref(true)
const showModal = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)
const showDeleteModal = ref(false)
const deleteId = ref<string | null>(null)
const deleting = ref(false)
const activeTab = ref<'uz' | 'ru' | 'en'>('uz')

const form = ref({
  title_uz: '', title_ru: '', title_en: '',
  content_uz: '', content_ru: '', content_en: '',
  is_active: true,
  published_at: '',
  expires_at: '',
})

onMounted(async () => {
  try {
    announcements.value = await api.get<Announcement[]>('/api/admin/announcements')
  } finally { loading.value = false }
})

function openCreate() {
  editingId.value = null
  Object.assign(form.value, {
    title_uz: '', title_ru: '', title_en: '',
    content_uz: '', content_ru: '', content_en: '',
    is_active: true, published_at: '', expires_at: '',
  })
  activeTab.value = 'uz'
  showModal.value = true
}

function openEdit(ann: Announcement) {
  editingId.value = ann.id
  Object.assign(form.value, {
    title_uz: ann.title_uz, title_ru: ann.title_ru, title_en: ann.title_en,
    content_uz: ann.content_uz || '', content_ru: ann.content_ru || '', content_en: ann.content_en || '',
    is_active: ann.is_active,
    published_at: ann.published_at ? ann.published_at.slice(0, 16) : '',
    expires_at: ann.expires_at ? ann.expires_at.slice(0, 16) : '',
  })
  activeTab.value = 'uz'
  showModal.value = true
}

async function save() {
  if (!form.value.title_uz) return
  saving.value = true
  try {
    const payload = {
      ...form.value,
      published_at: form.value.published_at || null,
      expires_at: form.value.expires_at || null,
    }
    if (editingId.value) {
      const updated = await api.put<Announcement>(`/api/admin/announcements/${editingId.value}`, payload)
      const idx = announcements.value.findIndex((a) => a.id === editingId.value)
      if (idx !== -1) announcements.value[idx] = updated
      toast.success(t('admin.announcements.updated'))
    } else {
      const created = await api.post<Announcement>('/api/admin/announcements', payload)
      announcements.value.unshift(created)
      toast.success(t('admin.announcements.created'))
    }
    showModal.value = false
  } catch { toast.error('Saqlashda xatolik') }
  finally { saving.value = false }
}

function confirmDelete(id: string) {
  deleteId.value = id; showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteId.value) return
  deleting.value = true
  try {
    await api.delete(`/api/admin/announcements/${deleteId.value}`)
    announcements.value = announcements.value.filter((a) => a.id !== deleteId.value)
    toast.success(t('admin.announcements.deleted'))
    showDeleteModal.value = false
  } catch { toast.error('O\'chirishda xatolik') }
  finally { deleting.value = false }
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.announcements.title') }}</h1>
      <AppButton @click="openCreate">
        <Plus :size="15" class="mr-1" />{{ t('admin.announcements.create') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <AppSpinner :size="32" class="text-primary-500" />
    </div>

    <div v-else class="flex flex-col gap-3">
      <div
        v-for="ann in announcements"
        :key="ann.id"
        class="flex items-start justify-between gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800"
      >
        <div class="flex-1 min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="font-medium text-slate-800 dark:text-slate-200">{{ ann.title_uz || ann.title_en }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium"
              :class="ann.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-700'"
            >
              {{ ann.is_active ? t('common.active') : t('common.inactive') }}
            </span>
          </div>
          <div class="mt-1 flex flex-wrap gap-3 text-xs text-slate-500">
            <span>{{ t('admin.announcements.publishedAt') }}: {{ ann.published_at ? formatDateShort(ann.published_at) : '—' }}</span>
            <span v-if="ann.expires_at">{{ t('admin.announcements.expiresAt') }}: {{ formatDateShort(ann.expires_at) }}</span>
            <span>{{ formatDateShort(ann.created_at) }}</span>
          </div>
        </div>
        <div class="flex gap-1.5 shrink-0">
          <button class="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700" @click="openEdit(ann)">
            <Pencil :size="14" />
          </button>
          <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(ann.id)">
            <Trash2 :size="14" />
          </button>
        </div>
      </div>
      <div v-if="!announcements.length" class="rounded-xl border border-slate-200 p-8 text-center text-slate-400 dark:border-slate-700">
        {{ t('common.no_data') }}
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Teleport v-if="showModal" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showModal = false" />
        <div class="relative flex w-full max-w-lg flex-col rounded-2xl bg-white shadow-xl dark:bg-slate-800" style="max-height: 85vh">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h3 class="font-semibold text-slate-900 dark:text-white">
              {{ editingId ? t('admin.announcements.edit') : t('admin.announcements.create') }}
            </h3>
            <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700" @click="showModal = false">
              <X :size="18" />
            </button>
          </div>
          <div class="overflow-y-auto p-6">
            <!-- Lang tabs -->
            <div class="mb-4 flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 dark:border-slate-700 dark:bg-slate-800/50">
              <button
                v-for="lang in ['uz', 'ru', 'en']"
                :key="lang"
                class="rounded-md px-4 py-1.5 text-sm font-medium transition"
                :class="activeTab === lang ? 'bg-white shadow-sm text-slate-900 dark:bg-slate-700 dark:text-white' : 'text-slate-500'"
                @click="activeTab = lang as 'uz' | 'ru' | 'en'"
              >
                {{ lang.toUpperCase() }}
              </button>
            </div>

            <div class="flex flex-col gap-4">
              <div>
                <label class="label-base">{{ t('admin.announcements.titleLabel') }}</label>
                <input
                  v-model="(form as any)[`title_${activeTab}`]"
                  class="input-base w-full"
                  :placeholder="`Sarlavha (${activeTab})`"
                />
              </div>
              <div>
                <label class="label-base">{{ t('admin.announcements.contentLabel') }}</label>
                <textarea
                  v-model="(form as any)[`content_${activeTab}`]"
                  rows="4"
                  class="input-base w-full resize-none"
                  :placeholder="`Kontent (${activeTab})`"
                />
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="label-base">{{ t('admin.announcements.publishedAt') }}</label>
                  <input v-model="form.published_at" type="datetime-local" class="input-base w-full" />
                </div>
                <div>
                  <label class="label-base">{{ t('admin.announcements.expiresAt') }} ({{ t('common.optional') }})</label>
                  <input v-model="form.expires_at" type="datetime-local" class="input-base w-full" />
                </div>
              </div>
              <label class="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                <input v-model="form.is_active" type="checkbox" class="rounded" />
                {{ t('common.active') }}
              </label>
            </div>
          </div>
          <div class="flex justify-end gap-3 border-t border-slate-200 px-6 py-4 dark:border-slate-700">
            <AppButton variant="ghost" @click="showModal = false">{{ t('common.cancel') }}</AppButton>
            <AppButton :loading="saving" @click="save">{{ t('common.save') }}</AppButton>
          </div>
        </div>
      </div>
    </Teleport>

    <ConfirmModal
      v-if="showDeleteModal"
      :title="t('common.delete')"
      :message="t('common.delete_confirm_text')"
      :confirm-label="t('common.delete')"
      :loading="deleting"
      danger
      @confirm="doDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>
