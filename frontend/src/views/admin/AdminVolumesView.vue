<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, BookOpen, ChevronRight, FileImage } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import type { Volume } from '@/types/volume'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'
import AssignArticlesModal from '@/components/admin/AssignArticlesModal.vue'

const { t } = useI18n()
const toast = useToast()

interface Issue {
  id: string
  volume_id: string
  number: number
  published_date?: string
  cover_image_url?: string
  article_count?: number
}

const volumes = ref<(Volume & { issues: Issue[] })[]>([])
const loading = ref(true)
const selectedVolumeId = ref<string | null>(null)
const showVolumeForm = ref(false)
const showIssueForm = ref(false)
const showDeleteVolumeModal = ref(false)
const deleteVolumeId = ref<string | null>(null)
const showAssignModal = ref(false)
const assignIssueId = ref<string | null>(null)
const saving = ref(false)

const volumeForm = reactive({ number: '', year: '', is_current: false, editId: '' })
const issueForm = reactive({ number: '', published_date: '' })

const selectedVolume = ref<(Volume & { issues: Issue[] }) | null>(null)

onMounted(async () => {
  try {
    volumes.value = await api.get<(Volume & { issues: Issue[] })[]>('/api/volumes')
    if (volumes.value.length) selectVolume(volumes.value[0])
  } finally {
    loading.value = false }
})

function selectVolume(vol: Volume & { issues: Issue[] }) {
  selectedVolumeId.value = vol.id
  selectedVolume.value = vol
}

function startCreateVolume() {
  Object.assign(volumeForm, { number: '', year: new Date().getFullYear().toString(), is_current: false, editId: '' })
  showVolumeForm.value = true
}

function startEditVolume(vol: Volume) {
  Object.assign(volumeForm, { number: String(vol.number), year: String(vol.year), is_current: vol.is_current, editId: vol.id })
  showVolumeForm.value = true
}

async function saveVolume() {
  if (!volumeForm.number || !volumeForm.year) return
  saving.value = true
  try {
    const payload = {
      number: Number(volumeForm.number),
      year: Number(volumeForm.year),
      is_current: volumeForm.is_current,
    }
    if (volumeForm.editId) {
      const updated = await api.put<Volume>(`/api/volumes/${volumeForm.editId}`, payload)
      const idx = volumes.value.findIndex((v) => v.id === volumeForm.editId)
      if (idx !== -1) volumes.value[idx] = { ...volumes.value[idx], ...updated }
      toast.success(t('admin.volumes.created'))
    } else {
      const created = await api.post<Volume>('/api/volumes', payload)
      volumes.value.unshift({ ...created, issues: [] })
    }
    showVolumeForm.value = false
  } catch { toast.error(t('admin.volumes.create_error')) }
  finally { saving.value = false }
}

function confirmDeleteVolume(id: string) {
  deleteVolumeId.value = id
  showDeleteVolumeModal.value = true
}

async function deleteVolume() {
  if (!deleteVolumeId.value) return
  saving.value = true
  try {
    await api.delete(`/api/volumes/${deleteVolumeId.value}`)
    volumes.value = volumes.value.filter((v) => v.id !== deleteVolumeId.value)
    if (selectedVolumeId.value === deleteVolumeId.value) {
      selectedVolume.value = null
      selectedVolumeId.value = null
    }
    toast.success('Jild o\'chirildi')
    showDeleteVolumeModal.value = false
  } catch { toast.error('O\'chirishda xatolik') }
  finally { saving.value = false }
}

async function saveIssue() {
  if (!selectedVolumeId.value || !issueForm.number) return
  saving.value = true
  try {
    const issue = await api.post<Issue>(`/api/volumes/${selectedVolumeId.value}/issues`, {
      number: Number(issueForm.number),
      published_date: issueForm.published_date || null,
    })
    if (selectedVolume.value) {
      selectedVolume.value.issues.push(issue)
    }
    showIssueForm.value = false
    toast.success(t('admin.volumes.createIssue') + ' yaratildi')
  } catch { toast.error('Sonni yaratishda xatolik') }
  finally { saving.value = false }
}

function openAssignModal(issueId: string) {
  assignIssueId.value = issueId
  showAssignModal.value = true
}

function onAssigned() {
  // Reload issues for current volume
  if (selectedVolumeId.value) {
    api.get<any>(`/api/volumes/${selectedVolumeId.value}`).then((data) => {
      if (selectedVolume.value) {
        selectedVolume.value.issues = data.issues || []
      }
    })
  }
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.volumes.title') }}</h1>
      <AppButton @click="startCreateVolume">
        <Plus :size="15" class="mr-1" />{{ t('admin.volumes.add') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <AppSpinner :size="32" class="text-primary-500" />
    </div>

    <div v-else class="flex gap-6">
      <!-- Left: Volumes list -->
      <div class="w-72 shrink-0">
        <div class="flex flex-col gap-2">
          <div
            v-for="vol in volumes"
            :key="vol.id"
            class="cursor-pointer rounded-xl border p-4 transition"
            :class="selectedVolumeId === vol.id
              ? 'border-primary-400 bg-primary-50 dark:border-primary-700 dark:bg-primary-950/30'
              : 'border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800'"
            @click="selectVolume(vol)"
          >
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <BookOpen :size="16" class="text-primary-500" />
                <div>
                  <p class="text-sm font-semibold text-slate-800 dark:text-slate-200">
                    Vol. {{ vol.number }} ({{ vol.year }})
                    <span v-if="vol.is_current" class="ml-1.5 rounded-full bg-emerald-100 px-1.5 py-0.5 text-xs font-medium text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-400">
                      {{ t('admin.volumes.current') }}
                    </span>
                  </p>
                  <p class="text-xs text-slate-500">{{ vol.issues.length }} {{ t('admin.volumes.issues') }}</p>
                </div>
              </div>
              <ChevronRight :size="14" class="text-slate-400" />
            </div>
            <div class="mt-2 flex gap-2" @click.stop>
              <button class="text-xs text-slate-400 hover:text-indigo-600" @click="startEditVolume(vol)">
                <Pencil :size="13" />
              </button>
              <button class="text-xs text-slate-400 hover:text-red-600" @click="confirmDeleteVolume(vol.id)">
                <Trash2 :size="13" />
              </button>
            </div>
          </div>
          <div v-if="!volumes.length" class="rounded-xl border border-slate-200 p-6 text-center text-sm text-slate-400 dark:border-slate-700">
            {{ t('common.no_data') }}
          </div>
        </div>
      </div>

      <!-- Right: Issues panel -->
      <div class="flex-1">
        <div v-if="!selectedVolume" class="flex h-48 items-center justify-center rounded-xl border border-dashed border-slate-200 text-slate-400 dark:border-slate-700">
          Jildni tanlang
        </div>
        <div v-else>
          <div class="mb-4 flex items-center justify-between">
            <h2 class="font-semibold text-slate-800 dark:text-white">
              Vol. {{ selectedVolume.number }} — {{ t('admin.volumes.issuesTitle') }}
            </h2>
            <AppButton variant="secondary" size="sm" @click="showIssueForm = !showIssueForm">
              <Plus :size="14" class="mr-1" />{{ t('admin.volumes.createIssue') }}
            </AppButton>
          </div>

          <!-- Create issue inline form -->
          <div v-if="showIssueForm" class="mb-4 rounded-xl border border-primary-200 bg-primary-50/50 p-4 dark:border-primary-800 dark:bg-primary-950/20">
            <div class="flex flex-wrap gap-4">
              <div>
                <label class="mb-1 block text-xs font-medium text-slate-700 dark:text-slate-300">{{ t('admin.volumes.col_number') }}</label>
                <input v-model="issueForm.number" type="number" min="1" class="input-base w-24" placeholder="1" />
              </div>
              <div>
                <label class="mb-1 block text-xs font-medium text-slate-700 dark:text-slate-300">{{ t('articles.published') }}</label>
                <input v-model="issueForm.published_date" type="date" class="input-base" />
              </div>
            </div>
            <div class="mt-3 flex gap-2">
              <AppButton size="sm" :loading="saving" @click="saveIssue">{{ t('common.create') }}</AppButton>
              <AppButton variant="ghost" size="sm" @click="showIssueForm = false">{{ t('common.cancel') }}</AppButton>
            </div>
          </div>

          <!-- Issues grid -->
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="issue in selectedVolume.issues"
              :key="issue.id"
              class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800"
            >
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-semibold text-slate-800 dark:text-white">
                    {{ t('archive.issue_label', { number: issue.number }) }}
                  </p>
                  <p v-if="issue.published_date" class="text-xs text-slate-500">
                    {{ issue.published_date.slice(0, 10) }}
                  </p>
                  <p class="mt-1 text-xs text-slate-500">
                    {{ issue.article_count ?? 0 }} {{ t('archive.articles') }}
                  </p>
                </div>
                <div v-if="issue.cover_image_url" class="h-12 w-10 overflow-hidden rounded-md border border-slate-200 dark:border-slate-700">
                  <img :src="issue.cover_image_url" class="h-full w-full object-cover" alt="" />
                </div>
                <div v-else class="flex h-12 w-10 items-center justify-center rounded-md border border-dashed border-slate-300 dark:border-slate-600">
                  <FileImage :size="16" class="text-slate-400" />
                </div>
              </div>
              <button
                class="mt-3 w-full rounded-lg border border-primary-200 py-1.5 text-xs font-medium text-primary-600 hover:bg-primary-50 dark:border-primary-800 dark:text-primary-400 dark:hover:bg-primary-950/30"
                @click="openAssignModal(issue.id)"
              >
                {{ t('admin.volumes.assignArticles') }}
              </button>
            </div>
            <div
              v-if="!selectedVolume.issues.length"
              class="col-span-3 flex h-32 items-center justify-center rounded-xl border border-dashed border-slate-200 text-slate-400 dark:border-slate-700"
            >
              {{ t('admin.volumes.noIssues') }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Volume create/edit modal -->
    <Teleport v-if="showVolumeForm" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showVolumeForm = false" />
        <div class="relative w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800">
          <h3 class="mb-4 font-semibold text-slate-900 dark:text-white">
            {{ volumeForm.editId ? t('common.edit') : t('admin.volumes.add') }}
          </h3>
          <div class="flex flex-col gap-4">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('admin.volumes.number_label') }}</label>
              <input v-model="volumeForm.number" type="number" min="1" class="input-base w-full" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('admin.volumes.year_label') }}</label>
              <input v-model="volumeForm.year" type="number" class="input-base w-full" />
            </div>
            <label class="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
              <input v-model="volumeForm.is_current" type="checkbox" class="rounded" />
              {{ t('admin.volumes.is_current_label') }}
            </label>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <AppButton variant="ghost" @click="showVolumeForm = false">{{ t('common.cancel') }}</AppButton>
            <AppButton :loading="saving" @click="saveVolume">{{ t('common.save') }}</AppButton>
          </div>
        </div>
      </div>
    </Teleport>

    <ConfirmModal
      v-if="showDeleteVolumeModal"
      :title="t('common.delete')"
      message="Jildni o'chirishni istaysizmi? Barcha sonlar ham o'chadi."
      :confirm-label="t('common.delete')"
      :loading="saving"
      danger
      @confirm="deleteVolume"
      @cancel="showDeleteVolumeModal = false"
    />

    <AssignArticlesModal
      v-if="showAssignModal && assignIssueId"
      :issue-id="assignIssueId"
      @close="showAssignModal = false"
      @assigned="onAssigned"
    />
  </div>
</template>
