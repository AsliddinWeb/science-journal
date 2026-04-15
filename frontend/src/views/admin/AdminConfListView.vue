<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2 } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const router = useRouter()
const toast = useToast()
const localeStore = useLocaleStore()

interface Conference {
  id: string; title: Record<string, string>; year: number
  location?: string; is_active: boolean; cover_image_url?: string
  sessions: any[]
}

const items = ref<Conference[]>([])
const loading = ref(true)
const showDelete = ref(false)
const deleteId = ref<string | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await api.get<{ items: Conference[] }>('/api/admin/conferences?limit=100')
    items.value = data.items
  } catch {}
  finally { loading.value = false }
}

function confirmDelete(id: string) { deleteId.value = id; showDelete.value = true }
async function doDelete() {
  if (!deleteId.value) return
  deleting.value = true
  try {
    await api.delete(`/api/admin/conferences/${deleteId.value}`)
    items.value = items.value.filter(c => c.id !== deleteId.value)
    toast.success(t('admin.conferences.deleted'))
    showDelete.value = false
  } catch { toast.error("Xatolik") }
  finally { deleting.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.sidebar.conferences') }}</h1>
      <button class="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700" @click="router.push('/admin/conf/list/new')">
        <Plus :size="15" />{{ t('admin.conferences.create') }}
      </button>
    </div>

    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
      <div v-else-if="!items.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-5 py-3">{{ t('admin.articles.col_title') }}</th>
              <th class="px-4 py-3">Yil</th>
              <th class="px-4 py-3">Joylashuv</th>
              <th class="px-4 py-3">{{ t('admin.conferences.sessions') }}</th>
              <th class="px-4 py-3">{{ t('common.active') }}</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="conf in items" :key="conf.id" class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50">
              <td class="px-5 py-3">
                <div class="flex items-center gap-3">
                  <img v-if="conf.cover_image_url" :src="`/api/uploads/${conf.cover_image_url}`" class="h-10 w-8 shrink-0 rounded object-cover" />
                  <span class="font-medium text-slate-800 dark:text-slate-200">{{ getLocalizedField(conf.title, localeStore.current, '') }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-300">{{ conf.year }}</td>
              <td class="px-4 py-3 text-slate-500">{{ conf.location || '—' }}</td>
              <td class="px-4 py-3 text-slate-500">{{ (conf.sessions || []).length }}</td>
              <td class="px-4 py-3">
                <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="conf.is_active ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 'bg-slate-100 text-slate-500'">
                  {{ conf.is_active ? t('common.active') : t('common.inactive') }}
                </span>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <RouterLink :to="`/admin/conf/list/${conf.id}/edit`" class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30"><Pencil :size="14" /></RouterLink>
                  <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(conf.id)"><Trash2 :size="14" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ConfirmModal v-if="showDelete" :title="t('admin.conferences.delete_confirm')" :message="t('common.delete_confirm_text')" :loading="deleting" danger @confirm="doDelete" @cancel="showDelete = false" />
  </div>
</template>
