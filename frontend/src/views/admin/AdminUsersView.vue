<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, UserPlus, Trash2, ToggleLeft, ToggleRight, ChevronDown, Pencil, X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { formatDateShort } from '@/utils/formatDate'
import { useToast } from '@/composables/useToast'
import type { User, PaginatedResponse } from '@/types/user'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppPagination from '@/components/ui/AppPagination.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()

const users = ref<User[]>([])
const total = ref(0); const pages = ref(0); const page = ref(1)
const loading = ref(true)
const showDeleteModal = ref(false)
const deleteUserId = ref<string | null>(null)
const deleting = ref(false)
const showInviteModal = ref(false)
const inviteEmail = ref('')
const inviteLoading = ref(false)
const roleDropdownId = ref<string | null>(null)
const roleDropdownPos = ref({ top: 0, left: 0 })
const changingRoleId = ref<string | null>(null)
const togglingId = ref<string | null>(null)

const filters = reactive({ search: '', role: '', is_active: '' })

// Edit modal
const showEditModal = ref(false)
const editing = ref(false)
const editForm = reactive({
  id: '',
  full_name: '',
  email: '',
  affiliation: '',
  country: "O'zbekiston",
  orcid_id: '',
  role: 'reader' as string,
  is_active: true,
  is_verified: false,
})

function openEdit(user: User) {
  editForm.id = user.id
  editForm.full_name = user.full_name || ''
  editForm.email = user.email || ''
  editForm.affiliation = (user as any).affiliation || ''
  editForm.country = (user as any).country || "O'zbekiston"
  editForm.orcid_id = (user as any).orcid_id || ''
  editForm.role = (user as any).role || 'reader'
  editForm.is_active = !!(user as any).is_active
  editForm.is_verified = !!(user as any).is_verified
  showEditModal.value = true
}

async function saveEdit() {
  if (!editForm.id) return
  editing.value = true
  try {
    const payload = {
      full_name: editForm.full_name,
      email: editForm.email,
      affiliation: editForm.affiliation || null,
      country: editForm.country || null,
      orcid_id: editForm.orcid_id || null,
      role: editForm.role,
      is_active: editForm.is_active,
      is_verified: editForm.is_verified,
    }
    const updated = await api.patch<User>(`/api/admin/users/${editForm.id}`, payload)
    const idx = users.value.findIndex((u) => u.id === editForm.id)
    if (idx !== -1) users.value[idx] = updated
    toast.success('Saqlandi')
    showEditModal.value = false
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Xatolik'
    toast.error(typeof msg === 'string' ? msg : 'Xatolik')
  } finally {
    editing.value = false
  }
}

const ALL_ROLES = ['superadmin', 'editor', 'reviewer', 'author', 'reader']
const roleBadge: Record<string, string> = {
  superadmin: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
  editor: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  reviewer: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  author: 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400',
  reader: 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400',
}

function buildUrl() {
  let url = `/api/admin/users?page=${page.value}&limit=20`
  if (filters.role) url += `&role=${filters.role}`
  if (filters.search) url += `&search=${encodeURIComponent(filters.search)}`
  if (filters.is_active !== '') url += `&is_active=${filters.is_active}`
  return url
}

async function load() {
  loading.value = true
  try {
    const data = await api.get<PaginatedResponse<User>>(buildUrl())
    users.value = data.items; total.value = data.total; pages.value = data.pages
  } finally { loading.value = false }
}

function applyFilters() { page.value = 1; load() }

let timer: ReturnType<typeof setTimeout>
function onSearchInput() {
  clearTimeout(timer); timer = setTimeout(applyFilters, 350)
}

onMounted(load)

function toggleRoleDropdown(userId: string, event: MouseEvent) {
  if (roleDropdownId.value === userId) { roleDropdownId.value = null; return }
  const r = (event.currentTarget as HTMLElement).getBoundingClientRect()
  roleDropdownPos.value = { top: r.bottom + window.scrollY + 4, left: r.left + window.scrollX }
  roleDropdownId.value = userId
}

async function changeRole(userId: string, role: string) {
  changingRoleId.value = userId
  roleDropdownId.value = null
  try {
    await api.patch(`/api/admin/users/${userId}/role?role=${role}`)
    const u = users.value.find((u) => u.id === userId)
    if (u) (u as any).role = role
    toast.success(t('admin.users.changeRole') + ' muvaffaqiyatli')
  } catch { toast.error('Xatolik') }
  finally { changingRoleId.value = null }
}

async function toggleActive(user: User) {
  togglingId.value = user.id
  const newActive = !(user as any).is_active
  try {
    await api.patch(`/api/admin/users/${user.id}/active?active=${newActive}`)
    ;(user as any).is_active = newActive
    toast.success(newActive ? t('admin.users.activate') : t('admin.users.deactivate'))
  } catch { toast.error('Xatolik') }
  finally { togglingId.value = null }
}

function confirmDelete(id: string) {
  deleteUserId.value = id; showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteUserId.value) return
  deleting.value = true
  try {
    await api.delete(`/api/admin/users/${deleteUserId.value}`)
    users.value = users.value.filter((u) => u.id !== deleteUserId.value)
    toast.success('Foydalanuvchi o\'chirildi')
    showDeleteModal.value = false
  } catch { toast.error('O\'chirishda xatolik') }
  finally { deleting.value = false }
}

async function sendInvite() {
  if (!inviteEmail.value) return
  inviteLoading.value = true
  try {
    await api.post('/api/admin/users/invite-reviewer', { email: inviteEmail.value })
    toast.success('Taklif yuborildi')
    showInviteModal.value = false
    inviteEmail.value = ''
    load()
  } catch { toast.error('Taklif yuborishda xatolik') }
  finally { inviteLoading.value = false }
}

function getUserInitials(name: string) {
  return name.split(' ').slice(0, 2).map((p) => p[0]).join('').toUpperCase()
}
</script>

<template>
  <div>
    <div class="mb-6 flex flex-wrap items-center justify-between gap-4">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">{{ t('admin.users.title') }}</h1>
      <AppButton @click="showInviteModal = true">
        <UserPlus :size="15" class="mr-1" />{{ t('admin.users.inviteReviewer') }}
      </AppButton>
    </div>

    <!-- Filters -->
    <div class="mb-4 flex flex-wrap gap-3">
      <div class="relative flex-1 min-w-48">
        <Search :size="15" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          v-model="filters.search"
          type="search"
          :placeholder="t('admin.users.search_placeholder')"
          class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm outline-none focus:border-primary-400 focus:ring-2 focus:ring-primary-100 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
          @input="onSearchInput"
        />
      </div>
      <select
        v-model="filters.role"
        class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
        @change="applyFilters"
      >
        <option value="">{{ t('common.all') }} ({{ t('admin.users.filter_role') }})</option>
        <option v-for="r in ALL_ROLES" :key="r" :value="r">{{ r }}</option>
      </select>
      <select
        v-model="filters.is_active"
        class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200"
        @change="applyFilters"
      >
        <option value="">{{ t('common.all') }}</option>
        <option value="true">{{ t('common.active') }}</option>
        <option value="false">{{ t('common.inactive') }}</option>
      </select>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16">
        <AppSpinner :size="32" class="text-primary-500" />
      </div>
      <div v-else-if="!users.length" class="py-16 text-center text-slate-400">
        {{ t('common.no_data') }}
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-slate-200 dark:border-slate-700">
            <tr class="text-left text-xs font-medium uppercase text-slate-500">
              <th class="px-5 py-3">{{ t('admin.users.col_name') }}</th>
              <th class="px-4 py-3">{{ t('admin.users.col_email') }}</th>
              <th class="px-4 py-3">{{ t('admin.users.col_role') }}</th>
              <th class="px-4 py-3">{{ t('admin.users.col_affiliation') }}</th>
              <th class="px-4 py-3">{{ t('admin.users.col_registered') }}</th>
              <th class="px-4 py-3">{{ t('admin.users.col_active') }}</th>
              <th class="px-4 py-3" />
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/50"
            >
              <td class="px-5 py-3">
                <div class="flex items-center gap-3">
                  <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                    {{ getUserInitials(user.full_name) }}
                  </div>
                  <span class="font-medium text-slate-800 dark:text-slate-200">{{ user.full_name }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ user.email }}</td>
              <td class="px-4 py-3">
                <button
                  class="flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
                  :class="roleBadge[(user as any).role] || roleBadge.reader"
                  :disabled="changingRoleId === user.id"
                  @click="toggleRoleDropdown(user.id, $event)"
                >
                  {{ (user as any).role }}
                  <ChevronDown :size="10" />
                </button>
              </td>
              <td class="px-4 py-3 text-slate-500 dark:text-slate-400">{{ (user as any).affiliation || '—' }}</td>
              <td class="whitespace-nowrap px-4 py-3 text-slate-500 dark:text-slate-400">
                {{ formatDateShort(user.created_at) }}
              </td>
              <td class="px-4 py-3">
                <button
                  class="text-slate-400 transition hover:text-slate-600 dark:hover:text-slate-300"
                  :disabled="togglingId === user.id"
                  @click="toggleActive(user)"
                >
                  <component
                    :is="(user as any).is_active ? ToggleRight : ToggleLeft"
                    :size="22"
                    :class="(user as any).is_active ? 'text-emerald-500' : 'text-slate-400'"
                  />
                </button>
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-1">
                  <button
                    class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30"
                    :title="t('common.edit')"
                    @click="openEdit(user)"
                  >
                    <Pencil :size="14" />
                  </button>
                  <button
                    class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30"
                    :title="t('common.delete')"
                    @click="confirmDelete(user.id)"
                  >
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
      <AppPagination :page="page" :pages="pages" :total="total" :limit="20"
        @update:page="(p) => { page = p; load() }" />
    </div>

    <!-- Invite modal -->
    <Teleport v-if="showInviteModal" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showInviteModal = false" />
        <div class="relative w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800">
          <h3 class="mb-4 font-semibold text-slate-900 dark:text-white">{{ t('admin.users.inviteReviewer') }}</h3>
          <input
            v-model="inviteEmail"
            type="email"
            placeholder="reviewer@example.com"
            class="input-base w-full"
            @keydown.enter="sendInvite"
          />
          <div class="mt-4 flex justify-end gap-3">
            <AppButton variant="ghost" @click="showInviteModal = false">{{ t('common.cancel') }}</AppButton>
            <AppButton :loading="inviteLoading" @click="sendInvite">{{ t('common.invite') }}</AppButton>
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

    <!-- Edit user modal -->
    <Teleport v-if="showEditModal" to="body">
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50" @click="showEditModal = false" />
        <div class="relative w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl dark:bg-slate-800">
          <div class="mb-5 flex items-center justify-between">
            <h3 class="font-serif text-lg font-semibold text-slate-900 dark:text-white">
              {{ t('common.edit') }} — {{ editForm.full_name }}
            </h3>
            <button class="text-slate-400 hover:text-slate-600" @click="showEditModal = false">
              <X :size="18" />
            </button>
          </div>

          <div class="space-y-4">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label class="label-base">{{ t('admin.users.col_name') }}</label>
                <input v-model="editForm.full_name" type="text" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.users.col_email') }}</label>
                <input v-model="editForm.email" type="email" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.users.col_affiliation') }}</label>
                <input v-model="editForm.affiliation" type="text" class="input-base w-full" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.users.col_country') || 'Country' }}</label>
                <input v-model="editForm.country" type="text" class="input-base w-full" />
              </div>
              <div class="sm:col-span-2">
                <label class="label-base">ORCID</label>
                <input v-model="editForm.orcid_id" type="text" class="input-base w-full font-mono" placeholder="0000-0000-0000-0000" />
              </div>
              <div>
                <label class="label-base">{{ t('admin.users.col_role') }}</label>
                <select v-model="editForm.role" class="input-base w-full">
                  <option v-for="r in ALL_ROLES" :key="r" :value="r">{{ r }}</option>
                </select>
              </div>
              <div class="flex flex-col gap-2 pt-6">
                <label class="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                  <input v-model="editForm.is_active" type="checkbox" class="rounded" />
                  {{ t('common.active') }}
                </label>
                <label class="inline-flex cursor-pointer items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
                  <input v-model="editForm.is_verified" type="checkbox" class="rounded" />
                  Verified
                </label>
              </div>
            </div>
          </div>

          <div class="mt-6 flex justify-end gap-3">
            <AppButton variant="ghost" @click="showEditModal = false">{{ t('common.cancel') }}</AppButton>
            <AppButton :loading="editing" @click="saveEdit">{{ t('common.save') }}</AppButton>
          </div>
        </div>
      </div>
    </Teleport>

    <div v-if="roleDropdownId" class="fixed inset-0 z-10" @click="roleDropdownId = null" />

    <Teleport to="body">
      <div
        v-if="roleDropdownId"
        class="fixed z-50 min-w-36 rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-800"
        :style="{ top: roleDropdownPos.top + 'px', left: roleDropdownPos.left + 'px' }"
      >
        <button
          v-for="role in ALL_ROLES"
          :key="role"
          class="block w-full px-3 py-1.5 text-left text-xs hover:bg-slate-100 dark:hover:bg-slate-700"
          :class="users.find(u => u.id === roleDropdownId)?.role === role ? 'font-semibold text-primary-600' : 'text-slate-700 dark:text-slate-300'"
          @click="changeRole(roleDropdownId!, role)"
        >
          {{ role }}
        </button>
      </div>
    </Teleport>
  </div>
</template>
