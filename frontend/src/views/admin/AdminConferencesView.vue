<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, Eye, Pencil, Trash2, ChevronDown, Plus } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { formatDateShort } from '@/utils/formatDate'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import ArticleStatusBadge from '@/components/article/ArticleStatusBadge.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const localeStore = useLocaleStore()
const toast = useToast()
const router = useRouter()

interface Paper {
  id: string; title: Record<string, string>; status: string; language: string
  author?: { full_name: string }; doi?: string; pages?: string
  created_at: string; conference_id: string; session_id?: string
}
interface Conference { id: string; title: Record<string, string> }

const papers = ref<Paper[]>([])
const conferences = ref<Conference[]>([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const loading = ref(true)
const showDeleteModal = ref(false)
const deleteTargetId = ref<string | null>(null)
const deletingId = ref<string | null>(null)
const statusDropdownId = ref<string | null>(null)
const dropdownPos = ref({ top: 0, left: 0 })

const filters = reactive({ search: '', status: '', conference_id: '' })
const ALL_STATUSES = ['draft', 'submitted', 'accepted', 'rejected', 'published']

// Load all conferences for filter dropdown
async function loadConferences() {
  try {
    const data = await api.get<{ items: Conference[] }>('/api/admin/conferences?limit=100')
    conferences.value = data.items
  } catch {}
}

function buildUrl() {
  // Aggregate papers from all conferences
  const confId = filters.conference_id || (conferences.value[0]?.id || '')
  if (!confId) return ''
  let url = `/api/admin/conferences/${confId}/papers?page=${page.value}&limit=20`
  if (filters.status) url += `&status=${filters.status}`
  if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`
  return url
}

async function load() {
  loading.value = true
  try {
    if (!conferences.value.length) await loadConferences()

    if (!conferences.value.length) {
      papers.value = []
      total.value = 0
      pages.value = 0
      return
    }

    // If no conference filter, load from first conference (or all)
    if (filters.conference_id) {
      const url = `/api/admin/conferences/${filters.conference_id}/papers?page=${page.value}&limit=20${filters.status ? '&status=' + filters.status : ''}${filters.search ? '&search=' + encodeURIComponent(filters.search) : ''}`
      const data = await api.get<{ items: Paper[]; total: number; pages: number }>(url)
      papers.value = data.items
      total.value = data.total
      pages.value = data.pages
    } else {
      // Load from all conferences
      const allPapers: Paper[] = []
      for (const conf of conferences.value) {
        try {
          const data = await api.get<{ items: Paper[] }>(`/api/admin/conferences/${conf.id}/papers?limit=100${filters.status ? '&status=' + filters.status : ''}${filters.search ? '&search=' + encodeURIComponent(filters.search) : ''}`)
          allPapers.push(...data.items)
        } catch {}
      }
      papers.value = allPapers
      total.value = allPapers.length
      pages.value = 1
    }
  } finally { loading.value = false }
}

function applyFilters() { page.value = 1; load() }
let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput() { clearTimeout(searchTimer); searchTimer = setTimeout(applyFilters, 350) }

function confirmDelete(id: string) { deleteTargetId.value = id; showDeleteModal.value = true }
async function doDelete() {
  if (!deleteTargetId.value) return
  const paper = papers.value.find(p => p.id === deleteTargetId.value)
  if (!paper) return
  deletingId.value = deleteTargetId.value
  try {
    await api.delete(`/api/admin/conferences/${paper.conference_id}/papers/${deleteTargetId.value}`)
    papers.value = papers.value.filter(p => p.id !== deleteTargetId.value)
    toast.success("O'chirildi")
    showDeleteModal.value = false
  } catch { toast.error("Xatolik") }
  finally { deletingId.value = null }
}

async function changeStatus(paperId: string, newStatus: string) {
  const paper = papers.value.find(p => p.id === paperId)
  if (!paper) return
  statusDropdownId.value = null
  try {
    await api.patch(`/api/admin/conferences/${paper.conference_id}/papers/${paperId}/status`, { status: newStatus })
    toast.success("Holat o'zgartirildi")
    await load()
  } catch { toast.error("Xatolik") }
}

function toggleStatusDropdown(id: string, event: MouseEvent) {
  if (statusDropdownId.value === id) { statusDropdownId.value = null; return }
  const btn = (event.currentTarget as HTMLElement).getBoundingClientRect()
  dropdownPos.value = { top: btn.bottom + window.scrollY + 4, left: btn.left + window.scrollX }
  statusDropdownId.value = id
}

function getConfName(confId: string) {
  const c = conferences.value.find(c => c.id === confId)
  return c ? getLocalizedField(c.title, localeStore.current, '') : '—'
}

function editUrl(paper: Paper) {
  return `/admin/conferences/${paper.conference_id}/papers/${paper.id}/edit`
}

onMounted(load)
</script>

<template>
  <div>
    <!-- Header — aynan AdminArticlesView dek -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.sidebar.conferences') }}</h1>
      <button
        class="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        @click="router.push('/admin/conferences/new')"
      >
        <Plus :size="15" />{{ t('admin.conferences.paper_create') }}
      </button>
    </div>

    <!-- Filters — aynan AdminArticlesView dek -->
    <div class="mb-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-48">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input v-model="filters.search" type="search" :placeholder="t('admin.articles.search_placeholder')" class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @input="onSearchInput" />
      </div>
      <select v-model="filters.status" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @change="applyFilters">
        <option value="">{{ t('common.all') }} ({{ t('admin.articles.filter_status') }})</option>
        <option v-for="s in ALL_STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
      </select>
      <select v-model="filters.conference_id" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @change="applyFilters">
        <option value="">{{ t('common.all') }} ({{ t('admin.sidebar.conferences') }})</option>
        <option v-for="c in conferences" :key="c.id" :value="c.id">{{ getLocalizedField(c.title, localeStore.current, '') }}</option>
      </select>
    </div>

    <!-- Table — aynan AdminArticlesView dek -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
      <div v-else-if="!papers.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-5 py-3">{{ t('admin.articles.col_title') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_authors') }}</th>
              <th class="px-4 py-3">{{ t('admin.sidebar.conferences') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_submitted') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_status') }}</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr v-for="paper in papers" :key="paper.id" class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50">
              <td class="max-w-xs px-5 py-3">
                <p class="line-clamp-1 font-medium text-slate-800 dark:text-slate-200">
                  {{ (getLocalizedField(paper.title, localeStore.current) || '').slice(0, 60) || t('common.untitled') }}
                </p>
                <p v-if="paper.doi" class="mt-0.5 font-mono text-xs text-slate-400">{{ paper.doi }}</p>
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-300">{{ paper.author?.full_name || '—' }}</td>
              <td class="px-4 py-3 text-xs text-slate-500">{{ getConfName(paper.conference_id) }}</td>
              <td class="whitespace-nowrap px-4 py-3 text-slate-500">{{ formatDateShort(paper.created_at) }}</td>
              <td class="px-4 py-3">
                <button class="flex items-center gap-1 text-xs" @click="toggleStatusDropdown(paper.id, $event)">
                  <ArticleStatusBadge :status="paper.status" />
                  <ChevronDown :size="11" class="text-slate-400" />
                </button>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <RouterLink :to="editUrl(paper)" class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30"><Pencil :size="14" /></RouterLink>
                  <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(paper.id)"><Trash2 :size="14" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="pages > 1" class="mt-4">
      <AppPagination :page="page" :pages="pages" :total="total" :limit="20" @update:page="(p: number) => { page = p; load() }" />
    </div>

    <ConfirmModal v-if="showDeleteModal" :title="t('common.delete')" :message="t('common.delete_confirm_text')" :loading="!!deletingId" danger @confirm="doDelete" @cancel="showDeleteModal = false" />

    <div v-if="statusDropdownId" class="fixed inset-0 z-10" @click="statusDropdownId = null" />
    <Teleport to="body">
      <div v-if="statusDropdownId" class="fixed z-50 min-w-40 rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800" :style="{ top: dropdownPos.top + 'px', left: dropdownPos.left + 'px' }">
        <button v-for="s in ALL_STATUSES" :key="s" class="block w-full px-3 py-1.5 text-left text-xs hover:bg-slate-100 dark:hover:bg-slate-700" :class="papers.find(p => p.id === statusDropdownId)?.status === s ? 'font-semibold text-primary-600' : 'text-slate-700 dark:text-slate-300'" @click="changeStatus(statusDropdownId!, s)">
          {{ t(`author.status.${s}`) }}
        </button>
      </div>
    </Teleport>
  </div>
</template>
