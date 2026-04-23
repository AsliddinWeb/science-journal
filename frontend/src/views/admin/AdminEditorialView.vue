<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import {
  Plus, Pencil, Trash2, ChevronUp, ChevronDown,
  MapPin, Mail, Building2, GraduationCap,
} from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()
const router = useRouter()

interface BoardMember {
  id: string
  name: string
  title?: string
  role: string
  affiliation?: string
  country?: string
  degree?: string
  specialization?: string
  email?: string
  bio?: string
  orcid_id?: string
  photo_url?: string
  order: number
  is_active: boolean
}

const members = ref<BoardMember[]>([])
const loading = ref(true)
const showDeleteModal = ref(false)
const deleteId = ref<string | null>(null)
const deleting = ref(false)
const reordering = ref(false)

const roleLabel: Record<string, string> = {
  editor_in_chief: 'Bosh muharrir',
  associate_editor: "Muharrir o'rinbosari",
  section_editor: "Bo'lim muharriri",
  reviewer: 'Retsenzent',
}
const roleBadge: Record<string, string> = {
  editor_in_chief: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-300',
  associate_editor: 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300',
  section_editor: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300',
  reviewer: 'bg-slate-200 text-slate-700 dark:bg-slate-700 dark:text-slate-200',
}
const roleAccent: Record<string, string> = {
  editor_in_chief: 'from-amber-400 to-amber-600',
  associate_editor: 'from-violet-400 to-violet-600',
  section_editor: 'from-blue-400 to-blue-600',
  reviewer: 'from-slate-400 to-slate-600',
}

const ROLE_ORDER = ['editor_in_chief', 'associate_editor', 'section_editor', 'reviewer']
const grouped = computed(() => {
  const groups: Record<string, BoardMember[]> = {}
  for (const role of ROLE_ORDER) {
    groups[role] = members.value
      .filter(m => m.role === role)
      .sort((a, b) => a.order - b.order)
  }
  return groups
})

onMounted(async () => {
  try { members.value = await api.get<BoardMember[]>('/api/editorial/members') }
  finally { loading.value = false }
})

function goCreate() { router.push('/admin/editorial/new') }
function goEdit(m: BoardMember) { router.push(`/admin/editorial/${m.id}/edit`) }

function confirmDelete(id: string) { deleteId.value = id; showDeleteModal.value = true }

async function doDelete() {
  if (!deleteId.value) return
  deleting.value = true
  try {
    await api.delete(`/api/editorial/members/${deleteId.value}`)
    members.value = members.value.filter(m => m.id !== deleteId.value)
    toast.success(t('admin.editorial.removed'))
    showDeleteModal.value = false
  } catch { toast.error(t('admin.editorial.remove_error')) }
  finally { deleting.value = false }
}

async function moveUp(member: BoardMember) {
  const group = grouped.value[member.role]
  const idx = group.findIndex(m => m.id === member.id)
  if (idx <= 0) return
  const prev = group[idx - 1]
  const temp = member.order; member.order = prev.order; prev.order = temp
  await saveOrder()
}

async function moveDown(member: BoardMember) {
  const group = grouped.value[member.role]
  const idx = group.findIndex(m => m.id === member.id)
  if (idx >= group.length - 1) return
  const next = group[idx + 1]
  const temp = member.order; member.order = next.order; next.order = temp
  await saveOrder()
}

async function saveOrder() {
  reordering.value = true
  try {
    const sorted = [...members.value].sort((a, b) => a.order - b.order)
    await api.patch('/api/editorial/members/reorder', { ordered_ids: sorted.map(m => m.id) })
  } catch { toast.error('Tartibni saqlashda xatolik') }
  finally { reordering.value = false }
}

function initials(name: string) {
  return name.split(' ').slice(0, 2).map(p => p[0]).join('').toUpperCase()
}

function resolvePhoto(u?: string) {
  if (!u) return ''
  return u.startsWith('http') || u.startsWith('/') ? u : `/api/uploads/${u}`
}
</script>

<template>
  <div>
    <div class="mb-6 flex items-center justify-between gap-4">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
        {{ t('admin.editorial.title') }}
      </h1>
      <AppButton @click="goCreate">
        <Plus :size="15" class="mr-1" />{{ t('admin.editorial.addMember') }}
      </AppButton>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <AppSpinner :size="32" class="text-primary-500" />
    </div>

    <div v-else class="space-y-10">
      <section v-for="role in ROLE_ORDER" :key="role">
        <h2 class="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-500">
          <span class="h-2 w-2 rounded-full bg-gradient-to-br" :class="roleAccent[role]" />
          {{ roleLabel[role] }}
          <span class="text-slate-400">({{ grouped[role].length }})</span>
        </h2>

        <div v-if="grouped[role].length" class="grid grid-cols-1 gap-3">
          <article
            v-for="(m, idx) in grouped[role]"
            :key="m.id"
            class="group overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:border-primary-400 hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="flex items-stretch gap-0">
              <!-- Avatar strip -->
              <div class="shrink-0 bg-gradient-to-br" :class="roleAccent[role]">
                <div class="flex h-full w-28 items-center justify-center p-3">
                  <img
                    v-if="m.photo_url"
                    :src="resolvePhoto(m.photo_url)"
                    :alt="m.name"
                    class="h-20 w-20 rounded-full border-2 border-white object-cover shadow-md"
                  />
                  <div
                    v-else
                    class="flex h-20 w-20 items-center justify-center rounded-full border-2 border-white bg-white/20 text-xl font-bold text-white shadow-md backdrop-blur"
                  >
                    {{ initials(m.name) }}
                  </div>
                </div>
              </div>

              <!-- Main info -->
              <div class="flex-1 min-w-0 p-4">
                <div class="flex flex-wrap items-center gap-2">
                  <span v-if="m.title" class="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    {{ m.title }}
                  </span>
                  <span
                    class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
                    :class="roleBadge[m.role]"
                  >{{ roleLabel[m.role] }}</span>
                  <span
                    v-if="!m.is_active"
                    class="rounded-full bg-red-100 px-2 py-0.5 text-[10px] font-medium text-red-700 dark:bg-red-900/30 dark:text-red-300"
                  >Nofaol</span>
                </div>

                <h3 class="mt-1 font-serif text-base font-bold text-journal-800 dark:text-primary-300 sm:text-lg">
                  {{ m.name }}
                </h3>

                <p v-if="m.degree || m.specialization" class="mt-0.5 text-sm text-slate-600 dark:text-slate-300">
                  <span v-if="m.degree" class="font-medium">{{ m.degree }}</span>
                  <span v-if="m.degree && m.specialization"> · </span>
                  <span v-if="m.specialization">{{ m.specialization }}</span>
                </p>

                <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
                  <span v-if="m.affiliation" class="inline-flex items-center gap-1">
                    <Building2 :size="12" />{{ m.affiliation }}
                  </span>
                  <span v-if="m.country" class="inline-flex items-center gap-1">
                    <MapPin :size="12" />{{ m.country }}
                  </span>
                  <a
                    v-if="m.email"
                    :href="`mailto:${m.email}`"
                    class="inline-flex items-center gap-1 hover:text-primary-600"
                  >
                    <Mail :size="12" />{{ m.email }}
                  </a>
                  <a
                    v-if="m.orcid_id"
                    :href="`https://orcid.org/${m.orcid_id}`"
                    target="_blank"
                    rel="noopener"
                    class="inline-flex items-center gap-1 text-[#a6ce39] hover:underline"
                  >
                    <GraduationCap :size="12" />{{ m.orcid_id }}
                  </a>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex shrink-0 flex-col items-center justify-between gap-1 border-l border-slate-100 px-3 py-3 dark:border-slate-700">
                <div class="flex flex-col gap-0.5">
                  <button
                    class="rounded p-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-30 dark:hover:bg-slate-700"
                    :disabled="idx === 0 || reordering"
                    :title="'Yuqoriga'"
                    @click="moveUp(m)"
                  ><ChevronUp :size="14" /></button>
                  <button
                    class="rounded p-0.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 disabled:opacity-30 dark:hover:bg-slate-700"
                    :disabled="idx === grouped[role].length - 1 || reordering"
                    :title="'Pastga'"
                    @click="moveDown(m)"
                  ><ChevronDown :size="14" /></button>
                </div>
                <div class="flex flex-col gap-1">
                  <button
                    class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30"
                    :title="t('common.edit')"
                    @click="goEdit(m)"
                  ><Pencil :size="14" /></button>
                  <button
                    class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30"
                    :title="t('common.delete')"
                    @click="confirmDelete(m.id)"
                  ><Trash2 :size="14" /></button>
                </div>
              </div>
            </div>
          </article>
        </div>
        <p v-else class="text-sm text-slate-400">{{ t('common.no_data') }}</p>
      </section>
    </div>

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
