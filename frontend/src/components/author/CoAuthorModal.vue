<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { X, Search, UserPlus, AlertCircle, Loader2 } from 'lucide-vue-next'
import { api } from '@/composables/useApi'

export interface CoAuthorEntry {
  user_id?: string | null
  guest_name?: string | null
  guest_email?: string | null
  guest_affiliation?: string | null
  guest_country?: string | null
  guest_orcid?: string | null
  is_corresponding: boolean
}

interface UserResult {
  id: string
  full_name: string
  email: string
  affiliation?: string | null
  country?: string | null
  orcid_id?: string | null
  avatar_url?: string | null
}

const emit = defineEmits<{
  close: []
  add: [CoAuthorEntry]
}>()

const { t } = useI18n()

type Tab = 'search' | 'manual'
const tab = ref<Tab>('search')

// Search tab
const emailQuery = ref('')
const searchResults = ref<UserResult[]>([])
const searching = ref(false)
const searchError = ref('')
let searchTimer: ReturnType<typeof setTimeout>

watch(emailQuery, (val) => {
  clearTimeout(searchTimer)
  searchResults.value = []
  searchError.value = ''
  if (val.trim().length < 3) return
  searchTimer = setTimeout(doSearch, 400)
})

async function doSearch() {
  searching.value = true
  searchError.value = ''
  try {
    const data = await api.get<UserResult[]>(`/api/users/search?email=${encodeURIComponent(emailQuery.value)}`)
    searchResults.value = data
  } catch {
    searchError.value = t('common.error')
  } finally {
    searching.value = false
  }
}

function selectUser(user: UserResult) {
  emit('add', {
    user_id: user.id,
    guest_name: null,
    guest_email: null,
    guest_affiliation: null,
    guest_country: null,
    guest_orcid: null,
    is_corresponding: false,
  })
  emit('close')
}

// Manual tab
const manual = reactive({
  guest_name: '',
  guest_email: '',
  guest_affiliation: '',
  guest_country: '',
  guest_orcid: '',
})
const manualErrors = reactive({
  guest_name: '',
  guest_email: '',
})

function validateManual(): boolean {
  manualErrors.guest_name = ''
  manualErrors.guest_email = ''
  let ok = true
  if (!manual.guest_name.trim()) {
    manualErrors.guest_name = t('contact.error_required')
    ok = false
  }
  if (manual.guest_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(manual.guest_email)) {
    manualErrors.guest_email = t('contact.error_email')
    ok = false
  }
  return ok
}

function addManual() {
  if (!validateManual()) return
  emit('add', {
    user_id: null,
    guest_name: manual.guest_name.trim(),
    guest_email: manual.guest_email.trim() || null,
    guest_affiliation: manual.guest_affiliation.trim() || null,
    guest_country: manual.guest_country.trim() || null,
    guest_orcid: manual.guest_orcid.trim() || null,
    is_corresponding: false,
  })
  emit('close')
}

function initials(name: string) {
  return name.split(' ').filter(Boolean).slice(0, 2).map((w) => w[0].toUpperCase()).join('')
}
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-md rounded-2xl bg-white shadow-2xl dark:bg-slate-900">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-800">
          <h2 class="font-serif text-lg font-bold text-slate-900 dark:text-white">
            {{ t('author.submit.add_coauthor') }}
          </h2>
          <button
            type="button"
            class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800"
            @click="$emit('close')"
          >
            <X :size="18" />
          </button>
        </div>

        <!-- Tabs -->
        <div class="flex border-b border-slate-200 dark:border-slate-800">
          <button
            type="button"
            class="flex-1 py-3 text-sm font-medium transition-colors"
            :class="tab === 'search'
              ? 'border-b-2 border-primary-600 text-primary-700 dark:text-primary-400'
              : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'"
            @click="tab = 'search'"
          >
            {{ t('author.submit.coauthor_search') }}
          </button>
          <button
            type="button"
            class="flex-1 py-3 text-sm font-medium transition-colors"
            :class="tab === 'manual'
              ? 'border-b-2 border-primary-600 text-primary-700 dark:text-primary-400'
              : 'text-slate-500 hover:text-slate-800 dark:text-slate-400'"
            @click="tab = 'manual'"
          >
            {{ t('author.submit.coauthor_manual') }}
          </button>
        </div>

        <!-- Search tab -->
        <div v-if="tab === 'search'" class="p-5">
          <div class="relative mb-4">
            <Search :size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
            <input
              v-model="emailQuery"
              type="email"
              :placeholder="t('author.submit.coauthor_email_placeholder')"
              class="input-base pl-9"
              autofocus
            />
          </div>

          <div v-if="searching" class="flex justify-center py-8">
            <Loader2 :size="24" class="animate-spin text-slate-400" />
          </div>

          <div v-else-if="searchError" class="flex items-center gap-2 text-sm text-red-500">
            <AlertCircle :size="15" />{{ searchError }}
          </div>

          <div v-else-if="searchResults.length === 0 && emailQuery.length >= 3" class="py-8 text-center text-sm text-slate-400">
            {{ t('author.submit.coauthor_not_found') }}
          </div>

          <ul v-else class="divide-y divide-slate-100 dark:divide-slate-800">
            <li
              v-for="user in searchResults"
              :key="user.id"
              class="flex cursor-pointer items-center gap-3 rounded-lg px-2 py-3 transition-colors hover:bg-slate-50 dark:hover:bg-slate-800"
              @click="selectUser(user)"
            >
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ initials(user.full_name) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-slate-900 dark:text-white">{{ user.full_name }}</p>
                <p class="truncate text-xs text-slate-500">{{ user.email }}</p>
                <p v-if="user.affiliation" class="truncate text-xs text-slate-400">{{ user.affiliation }}</p>
              </div>
              <UserPlus :size="16" class="shrink-0 text-slate-400" />
            </li>
          </ul>
        </div>

        <!-- Manual tab -->
        <div v-else class="space-y-4 p-5">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.full_name') }} *
            </label>
            <input
              v-model="manual.guest_name"
              type="text"
              class="input-base"
              :class="{ 'border-red-400': manualErrors.guest_name }"
            />
            <p v-if="manualErrors.guest_name" class="mt-1 text-xs text-red-500">{{ manualErrors.guest_name }}</p>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('contact.email') }}</label>
            <input v-model="manual.guest_email" type="email" class="input-base" :class="{ 'border-red-400': manualErrors.guest_email }" />
            <p v-if="manualErrors.guest_email" class="mt-1 text-xs text-red-500">{{ manualErrors.guest_email }}</p>
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('auth.affiliation') }}</label>
            <input v-model="manual.guest_affiliation" type="text" class="input-base" />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('auth.country') }}</label>
            <input v-model="manual.guest_country" type="text" class="input-base" />
          </div>
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">{{ t('auth.orcid') }}</label>
            <input v-model="manual.guest_orcid" type="text" placeholder="0000-0000-0000-0000" class="input-base" />
          </div>

          <button type="button" class="btn-primary w-full" @click="addManual">
            <UserPlus :size="16" />{{ t('author.submit.add_coauthor') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
