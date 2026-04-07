<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { Search, User } from 'lucide-vue-next'
import { useApi } from '@/composables/useApi'

interface Reviewer {
  id: string
  full_name: string
  email: string
  affiliation: string | null
  avatar_url: string | null
}

interface PaginatedResponse<T> {
  items: T[]
  total: number
}

const props = defineProps<{ modelValue: Reviewer | null }>()
const emit = defineEmits<{
  'update:modelValue': [v: Reviewer | null]
}>()

const { t } = useI18n()
const api = useApi()

const query = ref(props.modelValue?.full_name ?? '')
const results = ref<Reviewer[]>([])
const open = ref(false)
const loading = ref(false)
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(query, (val) => {
  if (props.modelValue && val === props.modelValue.full_name) return
  if (debounceTimer) clearTimeout(debounceTimer)
  if (!val.trim()) { results.value = []; open.value = false; return }
  debounceTimer = setTimeout(() => search(val), 300)
})

async function search(term: string) {
  loading.value = true
  try {
    const data = await api.get<PaginatedResponse<Reviewer>>(
      `/api/admin/users?role=reviewer&search=${encodeURIComponent(term)}&limit=8`
    )
    results.value = data.items
    open.value = data.items.length > 0
  } catch {
    results.value = []
  } finally {
    loading.value = false
  }
}

function select(r: Reviewer) {
  emit('update:modelValue', r)
  query.value = r.full_name
  open.value = false
}

function clear() {
  emit('update:modelValue', null)
  query.value = ''
  results.value = []
}

function initials(name: string) {
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}
</script>

<template>
  <div class="relative">
    <div class="relative">
      <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
      <input
        v-model="query"
        type="text"
        class="w-full rounded-lg border border-slate-300 bg-white py-2 pl-9 pr-3 text-sm text-slate-900 placeholder-slate-400 focus:border-indigo-400 focus:outline-none focus:ring-2 focus:ring-indigo-400/20 dark:border-slate-600 dark:bg-slate-900 dark:text-white"
        :placeholder="t('review.searchReviewerPlaceholder')"
        @focus="open = results.length > 0"
        @blur="setTimeout(() => (open = false), 150)"
      />
      <div v-if="loading" class="absolute right-3 top-1/2 -translate-y-1/2">
        <div class="h-4 w-4 animate-spin rounded-full border-2 border-indigo-500 border-t-transparent" />
      </div>
    </div>

    <!-- Dropdown -->
    <Transition name="dropdown">
      <div
        v-if="open"
        class="absolute z-20 mt-1 w-full rounded-xl border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-800"
      >
        <button
          v-for="r in results"
          :key="r.id"
          type="button"
          class="flex w-full items-center gap-3 px-3 py-2.5 text-left hover:bg-slate-50 dark:hover:bg-slate-700"
          @mousedown.prevent="select(r)"
        >
          <!-- Avatar initials -->
          <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-xs font-bold text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
            {{ initials(r.full_name) }}
          </div>
          <div class="min-w-0 flex-1">
            <p class="truncate text-sm font-medium text-slate-900 dark:text-white">{{ r.full_name }}</p>
            <p class="truncate text-xs text-slate-500 dark:text-slate-400">{{ r.email }}</p>
            <p v-if="r.affiliation" class="truncate text-xs text-slate-400 dark:text-slate-500">{{ r.affiliation }}</p>
          </div>
        </button>
      </div>
    </Transition>

    <!-- Selected chip -->
    <div v-if="modelValue" class="mt-2 flex items-center gap-2 rounded-lg bg-indigo-50 px-3 py-2 dark:bg-indigo-900/20">
      <User class="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
      <span class="text-sm font-medium text-indigo-800 dark:text-indigo-300">{{ modelValue.full_name }}</span>
      <button class="ml-auto text-indigo-400 hover:text-indigo-600" @click="clear">×</button>
    </div>
  </div>
</template>

<style scoped>
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.15s, transform 0.15s; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }
</style>
