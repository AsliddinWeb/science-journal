<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, X, ExternalLink, Upload, Loader2, Image as ImageIcon } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()

interface IndexingItem {
  id: string
  name: string
  url: string
  logo_url?: string
  description?: string
  order: number
  is_active: boolean
  created_at: string
}

const items = ref<IndexingItem[]>([])
const loading = ref(true)
const showModal = ref(false)
const editingId = ref<string | null>(null)
const saving = ref(false)
const showDeleteModal = ref(false)
const deleteId = ref<string | null>(null)
const deleting = ref(false)
const uploadingLogo = ref(false)

const form = ref({
  name: '',
  url: '',
  logo_url: '',
  description: '',
  order: 0,
  is_active: true,
})

onMounted(async () => {
  try {
    items.value = await api.get<IndexingItem[]>('/api/admin/indexing')
  } finally { loading.value = false }
})

function openCreate() {
  editingId.value = null
  Object.assign(form.value, { name: '', url: '', logo_url: '', description: '', order: items.value.length, is_active: true })
  showModal.value = true
}

function openEdit(item: IndexingItem) {
  editingId.value = item.id
  Object.assign(form.value, { ...item })
  showModal.value = true
}

async function save() {
  if (!form.value.name || !form.value.url) return
  saving.value = true
  try {
    const payload = { ...form.value, logo_url: form.value.logo_url || null, description: form.value.description || null }
    if (editingId.value) {
      const updated = await api.put<IndexingItem>(`/api/admin/indexing/${editingId.value}`, payload)
      const idx = items.value.findIndex((i) => i.id === editingId.value)
      if (idx !== -1) items.value[idx] = updated
      toast.success(t('admin.indexing.updated'))
    } else {
      const created = await api.post<IndexingItem>('/api/admin/indexing', payload)
      items.value.push(created)
      toast.success(t('admin.indexing.created'))
    }
    showModal.value = false
  } catch { toast.error('Saqlashda xatolik') }
  finally { saving.value = false }
}

async function uploadLogo(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  uploadingLogo.value = true
  try {
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.post<{ s3_key: string; url: string }>('/api/upload/image', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    form.value.logo_url = res.url || `/api/uploads/${res.s3_key}`
    toast.success('Logo yuklandi')
  } catch {
    toast.error('Logo yuklanmadi')
  } finally {
    uploadingLogo.value = false
  }
}

function confirmDelete(id: string) {
  deleteId.value = id; showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteId.value) return
  deleting.value = true
  try {
    await api.delete(`/api/admin/indexing/${deleteId.value}`)
    items.value = items.value.filter((i) => i.id !== deleteId.value)
    toast.success(t('admin.indexing.deleted'))
    showDeleteModal.value = false
  } catch { toast.error('O\'chirishda xatolik') }
  finally { deleting.value = false }
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.indexing.title') }}</h1>
      <AppButton @click="openCreate">
        <Plus :size="15" class="mr-1" />{{ t('admin.indexing.add') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <AppSpinner :size="32" class="text-primary-500" />
    </div>

    <div v-else class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="item in items"
        :key="item.id"
        class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
      >
        <div class="flex items-start justify-between gap-3">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-700">
              <img v-if="item.logo_url" :src="item.logo_url" :alt="item.name" class="h-full w-full object-contain p-1" />
              <span v-else class="text-xs font-bold text-slate-400">{{ item.name.slice(0, 2).toUpperCase() }}</span>
            </div>
            <div>
              <p class="font-semibold text-slate-800 dark:text-slate-200">{{ item.name }}</p>
              <a :href="item.url" target="_blank" class="flex items-center gap-1 text-xs text-primary-600 hover:underline dark:text-primary-400">
                <ExternalLink :size="11" />{{ item.url.replace(/^https?:\/\//, '').slice(0, 30) }}
              </a>
            </div>
          </div>
          <span
            class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium"
            :class="item.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-500 dark:bg-slate-700'"
          >
            {{ item.is_active ? t('common.active') : t('common.inactive') }}
          </span>
        </div>
        <p v-if="item.description" class="mt-2 line-clamp-2 text-xs text-slate-500">{{ item.description }}</p>
        <div class="mt-3 flex justify-end gap-2">
          <button class="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700" @click="openEdit(item)">
            <Pencil :size="14" />
          </button>
          <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(item.id)">
            <Trash2 :size="14" />
          </button>
        </div>
      </div>
      <div v-if="!items.length" class="col-span-3 rounded-xl border border-dashed border-slate-200 p-8 text-center text-slate-400 dark:border-slate-700">
        {{ t('common.no_data') }}
      </div>
    </div>

    <!-- Modal -->
    <Teleport v-if="showModal" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showModal = false" />
        <div class="relative w-full max-w-md rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800">
          <div class="mb-4 flex items-center justify-between">
            <h3 class="font-semibold text-slate-900 dark:text-white">
              {{ editingId ? t('admin.indexing.edit') : t('admin.indexing.add') }}
            </h3>
            <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700" @click="showModal = false">
              <X :size="18" />
            </button>
          </div>
          <div class="flex flex-col gap-4">
            <div>
              <label class="label-base">{{ t('admin.indexing.nameLabel') }} *</label>
              <input v-model="form.name" class="input-base w-full" placeholder="Scopus, Web of Science..." />
            </div>
            <div>
              <label class="label-base">{{ t('admin.indexing.urlLabel') }} *</label>
              <input v-model="form.url" class="input-base w-full" placeholder="https://..." />
            </div>
            <div>
              <label class="label-base">{{ t('admin.indexing.logoLabel') }}</label>
              <!-- Preview -->
              <div v-if="form.logo_url" class="mb-2 flex items-center gap-3 rounded-lg border border-stone-200 bg-stone-50 p-3 dark:border-slate-700 dark:bg-slate-900">
                <img :src="form.logo_url" alt="logo" class="h-14 w-14 object-contain" />
                <div class="min-w-0 flex-1">
                  <p class="truncate text-xs text-slate-500">{{ form.logo_url }}</p>
                </div>
                <button class="rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-900/30" @click="form.logo_url = ''">
                  <X :size="14" />
                </button>
              </div>
              <!-- Upload area -->
              <label class="flex cursor-pointer items-center justify-center gap-2 rounded-lg border-2 border-dashed border-stone-300 bg-stone-50 px-4 py-4 transition hover:border-primary-400 hover:bg-primary-50 dark:border-slate-600 dark:bg-slate-900 dark:hover:border-primary-400 dark:hover:bg-slate-800">
                <Loader2 v-if="uploadingLogo" :size="18" class="animate-spin text-primary-500" />
                <Upload v-else :size="18" class="text-slate-400" />
                <span class="text-sm text-slate-600 dark:text-slate-300">
                  {{ uploadingLogo ? 'Yuklanmoqda...' : (form.logo_url ? 'Almashtirish' : 'Logo yuklash') }}
                </span>
                <input type="file" accept="image/*" class="hidden" @change="uploadLogo" />
              </label>
              <p class="mt-1 text-xs text-slate-400">PNG, JPG yoki WebP. Tavsiya: kvadrat, shaffof fon</p>
            </div>
            <div>
              <label class="label-base">{{ t('admin.indexing.descLabel') }}</label>
              <textarea v-model="form.description" rows="2" class="input-base w-full resize-none" />
            </div>
            <div class="flex gap-4">
              <div class="flex-1">
                <label class="label-base">{{ t('admin.indexing.orderLabel') }}</label>
                <input v-model.number="form.order" type="number" min="0" class="input-base w-full" />
              </div>
              <label class="flex items-center gap-2 pt-6 text-sm text-slate-700 dark:text-slate-300">
                <input v-model="form.is_active" type="checkbox" class="rounded" />
                {{ t('common.active') }}
              </label>
            </div>
          </div>
          <div class="mt-6 flex justify-end gap-3">
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
