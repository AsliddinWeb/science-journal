<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, GripVertical, X, ChevronUp, ChevronDown } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()

interface BoardMember {
  id: string
  name: string
  title?: string
  role: string
  affiliation?: string
  country?: string
  bio?: string
  orcid_id?: string
  photo_url?: string
  order: number
  is_active: boolean
}

const members = ref<BoardMember[]>([])
const loading = ref(true)
const showDrawer = ref(false)
const editingMember = ref<BoardMember | null>(null)
const showDeleteModal = ref(false)
const deleteId = ref<string | null>(null)
const deleting = ref(false)
const saving = ref(false)
const reordering = ref(false)

const form = ref({
  name: '',
  title: '',
  role: 'reviewer',
  affiliation: '',
  country: '',
  bio: '',
  orcid_id: '',
  photo_url: '',
  is_active: true,
  order: 0,
})

const ROLES = ['editor_in_chief', 'associate_editor', 'section_editor', 'reviewer']
const roleLabel: Record<string, string> = {
  editor_in_chief: 'Bosh muharrir',
  associate_editor: 'Muharrir o\'rinbosari',
  section_editor: 'Bo\'lim muharriri',
  reviewer: 'Retsenzent',
}
const roleBadge: Record<string, string> = {
  editor_in_chief: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
  associate_editor: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-400',
  section_editor: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  reviewer: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
}

const ROLE_ORDER = ['editor_in_chief', 'associate_editor', 'section_editor', 'reviewer']
const grouped = computed(() => {
  const groups: Record<string, BoardMember[]> = {}
  for (const role of ROLE_ORDER) {
    groups[role] = members.value.filter((m) => m.role === role).sort((a, b) => a.order - b.order)
  }
  return groups
})

onMounted(async () => {
  try { members.value = await api.get<BoardMember[]>('/api/editorial/members') }
  finally { loading.value = false }
})

function openCreateDrawer() {
  editingMember.value = null
  Object.assign(form.value, { name: '', title: '', role: 'reviewer', affiliation: '', country: '', bio: '', orcid_id: '', photo_url: '', is_active: true, order: members.value.length })
  showDrawer.value = true
}

function openEditDrawer(member: BoardMember) {
  editingMember.value = member
  Object.assign(form.value, { ...member })
  showDrawer.value = true
}

async function saveMember() {
  if (!form.value.name) return
  saving.value = true
  try {
    const payload = { ...form.value }
    if (editingMember.value) {
      const updated = await api.put<BoardMember>(`/api/editorial/members/${editingMember.value.id}`, payload)
      const idx = members.value.findIndex((m) => m.id === editingMember.value!.id)
      if (idx !== -1) members.value[idx] = updated
      toast.success(t('admin.editorial.saved'))
    } else {
      const created = await api.post<BoardMember>('/api/editorial/members', payload)
      members.value.push(created)
      toast.success(t('admin.editorial.addMember') + ' qo\'shildi')
    }
    showDrawer.value = false
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
    await api.delete(`/api/editorial/members/${deleteId.value}`)
    members.value = members.value.filter((m) => m.id !== deleteId.value)
    toast.success(t('admin.editorial.removed'))
    showDeleteModal.value = false
  } catch { toast.error(t('admin.editorial.remove_error')) }
  finally { deleting.value = false }
}

async function moveUp(member: BoardMember) {
  const group = grouped.value[member.role]
  const idx = group.findIndex((m) => m.id === member.id)
  if (idx <= 0) return
  const allIds = members.value.map((m) => m.id)
  // Swap orders
  const prev = group[idx - 1]
  const temp = member.order; member.order = prev.order; prev.order = temp
  await saveOrder()
}

async function moveDown(member: BoardMember) {
  const group = grouped.value[member.role]
  const idx = group.findIndex((m) => m.id === member.id)
  if (idx >= group.length - 1) return
  const next = group[idx + 1]
  const temp = member.order; member.order = next.order; next.order = temp
  await saveOrder()
}

async function saveOrder() {
  reordering.value = true
  try {
    const sorted = [...members.value].sort((a, b) => a.order - b.order)
    await api.patch('/api/editorial/members/reorder', { ordered_ids: sorted.map((m) => m.id) })
  } catch { toast.error('Tartibni saqlashda xatolik') }
  finally { reordering.value = false }
}

function getMemberInitials(name: string) {
  return name.split(' ').slice(0, 2).map((p) => p[0]).join('').toUpperCase()
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.editorial.title') }}</h1>
      <AppButton @click="openCreateDrawer">
        <Plus :size="15" class="mr-1" />{{ t('admin.editorial.addMember') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <AppSpinner :size="32" class="text-primary-500" />
    </div>

    <div v-else class="flex flex-col gap-8">
      <div v-for="role in ROLE_ORDER" :key="role">
        <h2 class="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-500">{{ roleLabel[role] }}</h2>
        <div class="flex flex-col gap-2">
          <div
            v-for="(member, idx) in grouped[role]"
            :key="member.id"
            class="flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-slate-800"
          >
            <!-- Avatar -->
            <div class="shrink-0">
              <img
                v-if="member.photo_url"
                :src="member.photo_url"
                class="h-10 w-10 rounded-full object-cover"
                alt=""
              />
              <div
                v-else
                class="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300"
              >
                {{ getMemberInitials(member.name) }}
              </div>
            </div>

            <!-- Info -->
            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <span class="font-medium text-slate-800 dark:text-slate-200">{{ member.name }}</span>
                <span v-if="member.title" class="text-sm text-slate-500">{{ member.title }}</span>
                <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="roleBadge[member.role]">
                  {{ roleLabel[member.role] }}
                </span>
              </div>
              <p class="text-xs text-slate-500">{{ [member.affiliation, member.country].filter(Boolean).join(' · ') }}</p>
            </div>

            <!-- Reorder -->
            <div class="flex flex-col gap-1">
              <button
                class="rounded p-0.5 text-slate-400 hover:text-slate-600 disabled:opacity-30"
                :disabled="idx === 0"
                @click="moveUp(member)"
              >
                <ChevronUp :size="14" />
              </button>
              <button
                class="rounded p-0.5 text-slate-400 hover:text-slate-600 disabled:opacity-30"
                :disabled="idx === grouped[role].length - 1"
                @click="moveDown(member)"
              >
                <ChevronDown :size="14" />
              </button>
            </div>

            <!-- Actions -->
            <div class="flex gap-1.5">
              <button class="rounded p-1.5 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700" @click="openEditDrawer(member)">
                <Pencil :size="14" />
              </button>
              <button class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30" @click="confirmDelete(member.id)">
                <Trash2 :size="14" />
              </button>
            </div>
          </div>
          <p v-if="!grouped[role].length" class="text-sm text-slate-400">{{ t('common.no_data') }}</p>
        </div>
      </div>
    </div>

    <!-- Slide-in drawer -->
    <Transition
      enter-active-class="transition-all duration-200"
      enter-from-class="opacity-0"
      leave-active-class="transition-all duration-200"
      leave-to-class="opacity-0"
    >
      <div v-if="showDrawer" class="fixed inset-0 z-50 flex justify-end">
        <div class="absolute inset-0 bg-black/40" @click="showDrawer = false" />
        <div class="relative flex w-full max-w-md flex-col bg-white shadow-2xl dark:bg-slate-800 overflow-y-auto">
          <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
            <h3 class="font-semibold text-slate-900 dark:text-white">
              {{ editingMember ? t('common.edit') : t('admin.editorial.addMember') }}
            </h3>
            <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700" @click="showDrawer = false">
              <X :size="18" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-6">
            <div class="flex flex-col gap-4">
              <div>
                <label class="label-base">{{ t('admin.editorial.name') }} *</label>
                <input v-model="form.name" class="input-base w-full" :placeholder="t('admin.editorial.name')" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.member_title') }}</label>
                <input v-model="form.title" class="input-base w-full" placeholder="Prof., Dr., ..." />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.role') }}</label>
                <select v-model="form.role" class="input-base w-full">
                  <option v-for="r in ROLES" :key="r" :value="r">{{ roleLabel[r] }}</option>
                </select>
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.affiliation') }}</label>
                <input v-model="form.affiliation" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.country') }}</label>
                <input v-model="form.country" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.bio') }}</label>
                <textarea v-model="form.bio" rows="3" class="input-base w-full resize-none" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.orcid') }}</label>
                <input v-model="form.orcid_id" class="input-base w-full" placeholder="0000-0000-0000-0000" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.editorial.photo') }} URL</label>
                <input v-model="form.photo_url" class="input-base w-full" placeholder="https://..." />
              </div>
              <label class="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                <input v-model="form.is_active" type="checkbox" class="rounded" />
                {{ t('common.active') }}
              </label>
            </div>
          </div>
          <div class="border-t border-slate-200 px-6 py-4 dark:border-slate-700">
            <div class="flex justify-end gap-3">
              <AppButton variant="ghost" @click="showDrawer = false">{{ t('common.cancel') }}</AppButton>
              <AppButton :loading="saving" @click="saveMember">{{ t('common.save') }}</AppButton>
            </div>
          </div>
        </div>
      </div>
    </Transition>

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
