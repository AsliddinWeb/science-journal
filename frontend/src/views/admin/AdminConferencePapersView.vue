<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Eye, Pencil, Trash2, ArrowLeft, Search, ChevronDown } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'
import type { ConferencePaper, Conference } from '@/types/conference'
import type { PaginatedResponse } from '@/types/article'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const toast = useToast()
const localeStore = useLocaleStore()

const confId = computed(() => route.params.id as string)
const conference = ref<Conference | null>(null)
const papers = ref<ConferencePaper[]>([])
const loading = ref(true)
const showDeleteModal = ref(false)
const deleteTargetId = ref<string | null>(null)
const deletingId = ref<string | null>(null)

const STATUSES = ['draft', 'submitted', 'accepted', 'rejected', 'published']
const statusFilter = ref('')
const searchQuery = ref('')

async function load() {
  loading.value = true
  try {
    const [conf, papersData] = await Promise.all([
      api.get<Conference>(`/api/conferences/${confId.value}`),
      api.get<PaginatedResponse<ConferencePaper>>(buildUrl()),
    ])
    conference.value = conf
    papers.value = papersData.items
  } finally { loading.value = false }
}

function buildUrl() {
  let url = `/api/admin/conferences/${confId.value}/papers?limit=100`
  if (statusFilter.value) url += `&status=${statusFilter.value}`
  if (searchQuery.value) url += `&search=${encodeURIComponent(searchQuery.value)}`
  return url
}

async function applyFilters() {
  loading.value = true
  try {
    const data = await api.get<PaginatedResponse<ConferencePaper>>(buildUrl())
    papers.value = data.items
  } finally { loading.value = false }
}

function confirmDelete(id: string) { deleteTargetId.value = id; showDeleteModal.value = true }

async function doDelete() {
  if (!deleteTargetId.value) return
  deletingId.value = deleteTargetId.value
  try {
    await api.delete(`/api/admin/conferences/${confId.value}/papers/${deleteTargetId.value}`)
    papers.value = papers.value.filter(p => p.id !== deleteTargetId.value)
    toast.success(t('admin.conferences.deleted'))
    showDeleteModal.value = false
  } catch { toast.error("Xatolik") }
  finally { deletingId.value = null }
}

async function changeStatus(paperId: string, status: string) {
  try {
    await api.patch(`/api/admin/conferences/${confId.value}/papers/${paperId}/status`, { status })
    toast.success(t('admin.conferences.updated'))
    await load()
  } catch { toast.error("Xatolik") }
}

let searchTimer: ReturnType<typeof setTimeout>
function onSearch() { clearTimeout(searchTimer); searchTimer = setTimeout(applyFilters, 350) }

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="router.push('/admin/conferences')">
          <ArrowLeft :size="16" />{{ t('common.back') }}
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ conference ? getLocalizedField(conference.title, localeStore.current, '') : '' }} — {{ t('admin.conferences.view_papers') }}
        </h1>
      </div>
      <AppButton @click="router.push(`/admin/conferences/${confId}/papers/new`)">
        <Plus :size="15" class="mr-1" />{{ t('admin.conferences.paper_create') }}
      </AppButton>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-48">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input v-model="searchQuery" type="search" placeholder="Qidirish..." class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-primary-400 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @input="onSearch" />
      </div>
      <select v-model="statusFilter" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @change="applyFilters">
        <option value="">{{ t('common.all') }}</option>
        <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
      </select>
    </div>

    <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
    <div v-else-if="!papers.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>

    <div v-else class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <table class="w-full text-sm">
        <thead class="border-b border-slate-200 dark:border-slate-700">
          <tr class="text-left text-xs font-medium uppercase text-slate-500">
            <th class="px-5 py-3">{{ t('admin.articles.col_title') }}</th>
            <th class="px-4 py-3">{{ t('admin.articles.col_authors') }}</th>
            <th class="px-4 py-3">{{ t('admin.articles.col_status') }}</th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          <tr v-for="paper in papers" :key="paper.id" class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50">
            <td class="px-5 py-3">
              <p class="font-medium text-slate-800 dark:text-slate-200 line-clamp-1">{{ getLocalizedField(paper.title, localeStore.current, '') }}</p>
            </td>
            <td class="px-4 py-3 text-slate-500">{{ paper.author?.full_name || '—' }}</td>
            <td class="px-4 py-3">
              <select :value="paper.status" class="rounded bg-transparent text-xs font-medium" @change="changeStatus(paper.id, ($event.target as HTMLSelectElement).value)">
                <option v-for="s in STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
              </select>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-1">
                <button class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30" @click="router.push(`/admin/conferences/${confId}/papers/${paper.id}/edit`)">
                  <Pencil :size="14" />
                </button>
                <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(paper.id)">
                  <Trash2 :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <ConfirmModal v-if="showDeleteModal" :title="t('admin.conferences.delete_confirm')" :message="t('common.delete_confirm_text')" :loading="!!deletingId" danger @confirm="doDelete" @cancel="showDeleteModal = false" />
  </div>
</template>
