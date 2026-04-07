<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Plus, Pencil, Trash2, X, Check } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useCache } from '@/composables/useCache'
import { useToast } from '@/composables/useToast'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import AppButton from '@/components/ui/AppButton.vue'
import ConfirmModal from '@/components/admin/ConfirmModal.vue'

const { t } = useI18n()
const toast = useToast()
const cache = useCache()

interface Category {
  id: string
  name_uz: string
  name_ru: string
  name_en: string
  slug: string
  order: number
}

const categories = ref<Category[]>([])
const loading = ref(true)
const saving = ref(false)
const deletingId = ref<string | null>(null)
const showDeleteModal = ref(false)
const deleteTargetId = ref<string | null>(null)

// Drawer state
const drawer = ref(false)
const editingId = ref<string | null>(null)

const form = ref({
  name_uz: '',
  name_ru: '',
  name_en: '',
  slug: '',
  order: 0,
})

async function load() {
  loading.value = true
  try {
    categories.value = await api.get<Category[]>('/api/categories')
  } finally {
    loading.value = false }
}

function openCreate() {
  editingId.value = null
  form.value = { name_uz: '', name_ru: '', name_en: '', slug: '', order: categories.value.length }
  drawer.value = true
}

function openEdit(cat: Category) {
  editingId.value = cat.id
  form.value = { name_uz: cat.name_uz, name_ru: cat.name_ru, name_en: cat.name_en, slug: cat.slug, order: cat.order }
  drawer.value = true
}

function closeDrawer() {
  drawer.value = false
  editingId.value = null
}

// Auto-generate slug from en name
function onNameEn() {
  if (!editingId.value && !form.value.slug) {
    form.value.slug = form.value.name_en
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .replace(/\s+/g, '-')
      .replace(/-+/g, '-')
      .trim()
  }
}

async function save() {
  if (!form.value.name_uz || !form.value.name_ru || !form.value.name_en) {
    toast.error("Barcha 3 tilda nom kiriting")
    return
  }
  saving.value = true
  try {
    if (editingId.value) {
      const updated = await api.put<Category>(`/api/categories/${editingId.value}`, form.value)
      const idx = categories.value.findIndex(c => c.id === editingId.value)
      if (idx !== -1) categories.value[idx] = updated
      toast.success(t('admin.categories.updated'))
    } else {
      const created = await api.post<Category>('/api/categories', form.value)
      categories.value.push(created)
      toast.success(t('admin.categories.created'))
    }
    cache.invalidatePrefix('categories:')
    closeDrawer()
  } catch {
    toast.error("Xatolik yuz berdi")
  } finally {
    saving.value = false }
}

function confirmDelete(id: string) {
  deleteTargetId.value = id
  showDeleteModal.value = true
}

async function doDelete() {
  if (!deleteTargetId.value) return
  deletingId.value = deleteTargetId.value
  try {
    await api.delete(`/api/categories/${deleteTargetId.value}`)
    categories.value = categories.value.filter(c => c.id !== deleteTargetId.value)
    cache.invalidatePrefix('categories:')
    toast.success(t('admin.categories.deleted'))
    showDeleteModal.value = false
  } catch {
    toast.error("O'chirishda xatolik")
  } finally {
    deletingId.value = null }
}

onMounted(load)
</script>

<template>
  <div>
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
        {{ t('admin.categories.title') }}
      </h1>
      <AppButton @click="openCreate">
        <Plus :size="15" class="mr-1" />{{ t('admin.categories.create') }}
      </AppButton>
    </div>

    <!-- Table -->
    <div class="rounded-xl border border-slate-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800">
      <div v-if="loading" class="flex justify-center py-16">
        <AppSpinner :size="32" class="text-primary-500" />
      </div>
      <div v-else-if="!categories.length" class="py-16 text-center text-slate-400">
        {{ t('common.no_data') }}
      </div>
      <table v-else class="w-full text-sm">
        <thead class="border-b border-slate-200 dark:border-slate-700">
          <tr class="text-left text-xs font-medium uppercase text-slate-500">
            <th class="px-5 py-3">{{ t('admin.categories.name_uz') }}</th>
            <th class="px-4 py-3">{{ t('admin.categories.name_ru') }}</th>
            <th class="px-4 py-3">{{ t('admin.categories.name_en') }}</th>
            <th class="px-4 py-3">Slug</th>
            <th class="px-4 py-3 text-center">{{ t('admin.categories.order') }}</th>
            <th class="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="cat in categories"
            :key="cat.id"
            class="border-b border-slate-100 last:border-0 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-700/40"
          >
            <td class="px-5 py-3 font-medium text-slate-800 dark:text-slate-200">{{ cat.name_uz }}</td>
            <td class="px-4 py-3 text-slate-600 dark:text-slate-300">{{ cat.name_ru }}</td>
            <td class="px-4 py-3 text-slate-600 dark:text-slate-300">{{ cat.name_en }}</td>
            <td class="px-4 py-3 font-mono text-xs text-slate-400">{{ cat.slug }}</td>
            <td class="px-4 py-3 text-center text-slate-500">{{ cat.order }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center justify-end gap-1">
                <button
                  class="rounded p-1.5 text-slate-400 hover:bg-amber-50 hover:text-amber-600 dark:hover:bg-amber-900/30"
                  :title="t('common.edit')"
                  @click="openEdit(cat)"
                >
                  <Pencil :size="14" />
                </button>
                <button
                  class="rounded p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/30"
                  :title="t('common.delete')"
                  @click="confirmDelete(cat.id)"
                >
                  <Trash2 :size="14" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Drawer -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-to-class="opacity-0"
      >
        <div v-if="drawer" class="fixed inset-0 z-40 flex justify-end bg-black/40" @click.self="closeDrawer">
          <Transition
            enter-active-class="transition-transform duration-200 ease-out"
            enter-from-class="translate-x-full"
            leave-active-class="transition-transform duration-150 ease-in"
            leave-to-class="translate-x-full"
          >
            <div v-if="drawer" class="relative flex h-full w-full max-w-md flex-col bg-white shadow-2xl dark:bg-slate-900">
              <!-- Drawer header -->
              <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
                <h2 class="text-base font-semibold text-slate-900 dark:text-white">
                  {{ editingId ? t('admin.categories.edit') : t('admin.categories.create') }}
                </h2>
                <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800" @click="closeDrawer">
                  <X :size="18" />
                </button>
              </div>

              <!-- Drawer body -->
              <div class="flex-1 overflow-y-auto px-6 py-5 space-y-4">

                <div>
                  <label class="label-base">{{ t('admin.categories.name_uz') }} <span class="text-red-500">*</span></label>
                  <input v-model="form.name_uz" class="input-base w-full" placeholder="O'zbekcha nom" />
                </div>

                <div>
                  <label class="label-base">{{ t('admin.categories.name_ru') }} <span class="text-red-500">*</span></label>
                  <input v-model="form.name_ru" class="input-base w-full" placeholder="Название на русском" />
                </div>

                <div>
                  <label class="label-base">{{ t('admin.categories.name_en') }} <span class="text-red-500">*</span></label>
                  <input v-model="form.name_en" class="input-base w-full" placeholder="English name" @input="onNameEn" />
                </div>

                <div>
                  <label class="label-base">Slug</label>
                  <input v-model="form.slug" class="input-base w-full font-mono text-sm" placeholder="natural-sciences" />
                  <p class="mt-1 text-xs text-slate-400">URL da ishlatiladi. Inglizcha nom asosida avtomatik yaratiladi</p>
                </div>

                <div>
                  <label class="label-base">{{ t('admin.categories.order') }}</label>
                  <input v-model.number="form.order" type="number" min="0" class="input-base w-24" />
                  <p class="mt-1 text-xs text-slate-400">Kichik raqam yuqorida ko'rinadi</p>
                </div>
              </div>

              <!-- Drawer footer -->
              <div class="border-t border-slate-200 px-6 py-4 dark:border-slate-700 flex justify-end gap-2">
                <AppButton variant="secondary" @click="closeDrawer">{{ t('common.cancel') }}</AppButton>
                <AppButton :loading="saving" @click="save">
                  <Check :size="15" class="mr-1" />{{ t('common.save') }}
                </AppButton>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- Delete confirm -->
    <ConfirmModal
      v-if="showDeleteModal"
      :title="t('admin.categories.delete_confirm')"
      :message="t('common.delete_confirm_text')"
      :loading="!!deletingId"
      danger
      @confirm="doDelete"
      @cancel="showDeleteModal = false"
    />
  </div>
</template>
