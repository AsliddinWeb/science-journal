<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, Eye, Pencil, Trash2, ChevronDown, Plus, ArrowLeft } from 'lucide-vue-next'
import { useRouter, useRoute } from 'vue-router'
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
const route = useRoute()

const confId = computed(() => route.params.id as string)

interface Conference { id: string; title: Record<string, string>; sessions: any[] }
interface Paper {
  id: string; title: Record<string, string>; status: string; language: string
  author?: { full_name: string }; doi?: string; pages?: string
  created_at: string; published_date?: string; session_id?: string
  view_count: number; download_count: number
}

const conference = ref<Conference | null>(null)
const papers = ref<Paper[]>([])
const total = ref(0)
const pages = ref(0)
const page = ref(1)
const loading = ref(true)
const selectedIds = ref<Set<string>>(new Set())
const showDeleteModal = ref(false)
const deleteTargetId = ref<string | null>(null)
const deletingId = ref<string | null>(null)
const changingStatusId = ref<string | null>(null)
const statusDropdownId = ref<string | null>(null)
const dropdownPos = ref({ top: 0, left: 0 })

const filters = reactive({ search: '', status: '', language: '' })

const ALL_STATUSES = ['draft', 'submitted', 'accepted', 'rejected', 'published']
const ALL_LANGUAGES = ['uz', 'ru', 'en']

function buildUrl() {
  let url = `/api/admin/conferences/${confId.value}/papers?page=${page.value}&limit=20`
  if (filters.status) url += `&status=${filters.status}`
  if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`
  if (filters.language) url += `&language=${filters.language}`
  return url
}

async function load() {
  loading.value = true
  selectedIds.value.clear()
  try {
    if (!conference.value) {
      conference.value = await api.get<Conference>(`/api/conferences/${confId.value}`)
    }
    const data = await api.get<{ items: Paper[]; total: number; pages: number }>(buildUrl())
    papers.value = data.items
    total.value = data.total
    pages.value = data.pages
  } finally { loading.value = false }
}

function applyFilters() { page.value = 1; load() }
let searchTimer: ReturnType<typeof setTimeout>
function onSearchInput() { clearTimeout(searchTimer); searchTimer = setTimeout(applyFilters, 350) }

onMounted(load)

function toggleSelect(id: string) { selectedIds.value.has(id) ? selectedIds.value.delete(id) : selectedIds.value.add(id) }
function toggleAll() { selectedIds.value.size === papers.value.length ? selectedIds.value.clear() : papers.value.forEach(p => selectedIds.value.add(p.id)) }
const allSelected = computed(() => papers.value.length > 0 && selectedIds.value.size === papers.value.length)

function confirmDelete(id: string) { deleteTargetId.value = id; showDeleteModal.value = true }
async function doDelete() {
  if (!deleteTargetId.value) return
  deletingId.value = deleteTargetId.value
  try {
    await api.delete(`/api/admin/conferences/${confId.value}/papers/${deleteTargetId.value}`)
    papers.value = papers.value.filter(p => p.id !== deleteTargetId.value)
    toast.success("O'chirildi")
    showDeleteModal.value = false
  } catch { toast.error("Xatolik") }
  finally { deletingId.value = null }
}

async function changeStatus(paperId: string, newStatus: string) {
  changingStatusId.value = paperId
  statusDropdownId.value = null
  try {
    await api.patch(`/api/admin/conferences/${confId.value}/papers/${paperId}/status`, { status: newStatus })
    toast.success("Holat o'zgartirildi")
    await load()
  } catch { toast.error("Xatolik") }
  finally { changingStatusId.value = null }
}

function toggleStatusDropdown(id: string, event: MouseEvent) {
  if (statusDropdownId.value === id) { statusDropdownId.value = null; return }
  const btn = (event.currentTarget as HTMLElement).getBoundingClientRect()
  dropdownPos.value = { top: btn.bottom + window.scrollY + 4, left: btn.left + window.scrollX }
  statusDropdownId.value = id
}

const confTitle = computed(() => conference.value ? getLocalizedField(conference.value.title, localeStore.current, '') : '')
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-3">
        <button class="text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300" @click="router.push('/admin/conferences')">
          <ArrowLeft :size="16" />
        </button>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ confTitle }} — {{ t('admin.conferences.view_papers') }}
        </h1>
      </div>
      <button
        class="flex items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
        @click="router.push(`/admin/conferences/${confId}/papers/new`)"
      >
        <Plus :size="15" />{{ t('admin.conferences.paper_create') }}
      </button>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-48">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="filters.search"
          type="search"
          :placeholder="t('admin.articles.search_placeholder')"
          class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          @input="onSearchInput"
        />
      </div>
      <select v-model="filters.status" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @change="applyFilters">
        <option value="">{{ t('common.all') }} ({{ t('admin.articles.filter_status') }})</option>
        <option v-for="s in ALL_STATUSES" :key="s" :value="s">{{ t(`author.status.${s}`) }}</option>
      </select>
      <select v-model="filters.language" class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200" @change="applyFilters">
        <option value="">{{ t('common.all') }} ({{ t('articles.filter_language') }})</option>
        <option v-for="l in ALL_LANGUAGES" :key="l" :value="l">{{ l.toUpperCase() }}</option>
      </select>
    </div>

    <!-- Bulk actions -->
    <div v-if="selectedIds.size > 0" class="mb-4 flex items-center gap-3 rounded-lg border border-primary-200 bg-primary-50 px-4 py-2.5 dark:border-primary-800 dark:bg-primary-950/30">
      <span class="text-sm font-medium text-primary-700 dark:text-primary-300">{{ selectedIds.size }} {{ t('admin.articles.selected') }}</span>
      <div class="flex-1" />
      <button class="text-sm text-red-600 hover:underline dark:text-red-400" @click="selectedIds.clear()">{{ t('common.cancel') }}</button>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16"><AppSpinner :size="32" class="text-primary-500" /></div>
      <div v-else-if="!papers.length" class="py-16 text-center text-slate-400">{{ t('common.no_data') }}</div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-4 py-3"><input type="checkbox" :checked="allSelected" class="rounded" @change="toggleAll" /></th>
              <th class="px-4 py-3">{{ t('admin.articles.col_title') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_authors') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_submitted') }}</th>
              <th class="px-4 py-3">{{ t('admin.articles.col_status') }}</th>
              <th class="px-4 py-3">DOI</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="paper in papers"
              :key="paper.id"
              class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50"
              :class="selectedIds.has(paper.id) ? 'bg-primary-50/50 dark:bg-primary-950/20' : ''"
            >
              <td class="px-4 py-3"><input type="checkbox" :checked="selectedIds.has(paper.id)" class="rounded" @change="toggleSelect(paper.id)" /></td>
              <td class="max-w-xs px-4 py-3">
                <p class="line-clamp-1 font-medium text-slate-800 dark:text-slate-200">
                  {{ (getLocalizedField(paper.title, localeStore.current) || '').slice(0, 60) || t('common.untitled') }}
                </p>
                <p v-if="paper.pages" class="text-xs text-slate-400">{{ paper.pages }}-bet</p>
              </td>
              <td class="px-4 py-3 text-slate-600 dark:text-slate-300">{{ paper.author?.full_name || '—' }}</td>
              <td class="whitespace-nowrap px-4 py-3 text-slate-500 dark:text-slate-400">{{ formatDateShort(paper.created_at) }}</td>
              <td class="px-4 py-3">
                <button class="flex items-center gap-1 text-xs" :disabled="changingStatusId === paper.id" @click="toggleStatusDropdown(paper.id, $event)">
                  <ArticleStatusBadge :status="paper.status" />
                  <ChevronDown :size="11" class="text-slate-400" />
                </button>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-slate-400">{{ paper.doi || '—' }}</td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1.5">
                  <RouterLink :to="`/admin/conferences/${confId}/papers/${paper.id}/edit`" class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30" :title="t('common.edit')">
                    <Pencil :size="14" />
                  </RouterLink>
                  <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" :title="t('common.delete')" @click="confirmDelete(paper.id)">
                    <Trash2 :size="14" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="mt-4">
      <AppPagination :page="page" :pages="pages" :total="total" :limit="20" @update:page="(p: number) => { page = p; load() }" />
    </div>

    <ConfirmModal v-if="showDeleteModal" :title="t('common.delete')" :message="t('common.delete_confirm_text')" :confirm-label="t('common.delete')" :loading="!!deletingId" danger @confirm="doDelete" @cancel="showDeleteModal = false" />

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
