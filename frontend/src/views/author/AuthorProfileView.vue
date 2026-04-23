<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { AlertCircle, CheckCircle, Save, KeyRound, Loader2 } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import AvatarUpload from '@/components/upload/AvatarUpload.vue'

const { t } = useI18n()
const authStore = useAuthStore()

const user = computed(() => authStore.user)

// ─── Profile form ────────────────────────────────────────────────────
const profile = reactive({
  full_name: '',
  affiliation: '',
  country: "O'zbekiston",
  orcid_id: '',
})
const profileErrors = reactive({ full_name: '', orcid_id: '' })
const profileSaving = ref(false)
const profileSuccess = ref(false)
const profileError = ref('')

onMounted(() => {
  if (user.value) {
    profile.full_name = user.value.full_name ?? ''
    profile.affiliation = user.value.affiliation ?? ''
    profile.country = user.value.country || "O'zbekiston"
    profile.orcid_id = user.value.orcid_id ?? ''
  }
})

function validateProfile(): boolean {
  profileErrors.full_name = ''
  profileErrors.orcid_id = ''
  let ok = true
  if (!profile.full_name.trim()) {
    profileErrors.full_name = t('contact.error_required')
    ok = false
  }
  if (profile.orcid_id && !/^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/.test(profile.orcid_id)) {
    profileErrors.orcid_id = t('author.profile.orcid_invalid')
    ok = false
  }
  return ok
}

async function saveProfile() {
  if (!validateProfile()) return
  profileSaving.value = true
  profileSuccess.value = false
  profileError.value = ''
  try {
    const updated = await api.put('/api/users/me', {
      full_name: profile.full_name.trim(),
      affiliation: profile.affiliation.trim() || null,
      country: profile.country.trim() || null,
      orcid_id: profile.orcid_id.trim() || null,
    })
    authStore.setUser(updated as any)
    profileSuccess.value = true
    setTimeout(() => { profileSuccess.value = false }, 3000)
  } catch (e: any) {
    profileError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    profileSaving.value = false
  }
}

// ─── Password form ───────────────────────────────────────────────────
const passwords = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
})
const passwordErrors = reactive({ current_password: '', new_password: '', confirm_password: '' })
const passwordSaving = ref(false)
const passwordSuccess = ref(false)
const passwordError = ref('')

function validatePasswords(): boolean {
  passwordErrors.current_password = ''
  passwordErrors.new_password = ''
  passwordErrors.confirm_password = ''
  let ok = true
  if (!passwords.current_password) { passwordErrors.current_password = t('contact.error_required'); ok = false }
  if (passwords.new_password.length < 8) { passwordErrors.new_password = t('author.profile.password_min'); ok = false }
  if (passwords.new_password !== passwords.confirm_password) { passwordErrors.confirm_password = t('author.profile.password_mismatch'); ok = false }
  return ok
}

async function changePassword() {
  if (!validatePasswords()) return
  passwordSaving.value = true
  passwordSuccess.value = false
  passwordError.value = ''
  try {
    await api.post('/api/users/me/password', {
      current_password: passwords.current_password,
      new_password: passwords.new_password,
    })
    passwords.current_password = ''
    passwords.new_password = ''
    passwords.confirm_password = ''
    passwordSuccess.value = true
    setTimeout(() => { passwordSuccess.value = false }, 3000)
  } catch (e: any) {
    passwordError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    passwordSaving.value = false
  }
}

// ─── Avatar ──────────────────────────────────────────────────────────
async function onAvatarUploaded(url: string) {
  try {
    const updated = await api.put('/api/users/me', { avatar_url: url })
    authStore.setUser(updated as any)
  } catch {}
}
</script>

<template>
  <div class="min-h-screen bg-white dark:bg-slate-950">
    <!-- Header -->
    <div class="border-b border-slate-200 bg-slate-50 py-8 dark:border-slate-800 dark:bg-slate-900">
      <div class="mx-auto max-w-3xl px-4 sm:px-6 lg:px-8">
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('author.profile.title') }}
        </h1>
      </div>
    </div>

    <div class="mx-auto max-w-3xl space-y-8 px-4 py-8 sm:px-6 lg:px-8">

      <!-- Avatar section -->
      <div class="card p-6 text-center">
        <h2 class="mb-5 font-serif text-base font-bold text-slate-900 dark:text-white">
          {{ t('author.profile.avatar') }}
        </h2>
        <AvatarUpload
          :current-url="user?.avatar_url"
          :name="user?.full_name"
          @uploaded="onAvatarUploaded"
        />
      </div>

      <!-- Profile form -->
      <div class="card p-6">
        <h2 class="mb-5 font-serif text-base font-bold text-slate-900 dark:text-white">
          {{ t('author.profile.edit_profile') }}
        </h2>

        <div class="space-y-4">
          <!-- Full name -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.full_name') }} *
            </label>
            <input
              v-model="profile.full_name"
              type="text"
              class="input-base"
              :class="{ 'border-red-400': profileErrors.full_name }"
            />
            <p v-if="profileErrors.full_name" class="mt-1 text-xs text-red-500">{{ profileErrors.full_name }}</p>
          </div>

          <!-- Email (readonly) -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.email') }}
            </label>
            <input
              :value="user?.email"
              type="email"
              readonly
              class="input-base cursor-not-allowed opacity-60"
            />
          </div>

          <!-- Affiliation -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.affiliation') }}
            </label>
            <input v-model="profile.affiliation" type="text" class="input-base" />
          </div>

          <!-- Country -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.country') }}
            </label>
            <input v-model="profile.country" type="text" class="input-base" />
          </div>

          <!-- ORCID -->
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.orcid') }}
            </label>
            <input
              v-model="profile.orcid_id"
              type="text"
              placeholder="0000-0000-0000-0000"
              class="input-base font-mono"
              :class="{ 'border-red-400': profileErrors.orcid_id }"
            />
            <p v-if="profileErrors.orcid_id" class="mt-1 text-xs text-red-500">{{ profileErrors.orcid_id }}</p>
          </div>

          <!-- Success / Error -->
          <div v-if="profileSuccess" class="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <CheckCircle :size="16" />{{ t('author.profile.saved') }}
          </div>
          <div v-if="profileError" class="flex items-center gap-2 text-sm text-red-500">
            <AlertCircle :size="16" />{{ profileError }}
          </div>

          <button
            type="button"
            class="btn-primary"
            :disabled="profileSaving"
            @click="saveProfile"
          >
            <Loader2 v-if="profileSaving" :size="16" class="animate-spin" />
            <Save v-else :size="16" />
            {{ t('common.save') }}
          </button>
        </div>
      </div>

      <!-- Change password -->
      <div class="card p-6">
        <h2 class="mb-5 font-serif text-base font-bold text-slate-900 dark:text-white">
          <KeyRound :size="18" class="mr-2 inline text-primary-600 dark:text-primary-400" />
          {{ t('author.profile.change_password') }}
        </h2>

        <div class="space-y-4">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('author.profile.current_password') }}
            </label>
            <input
              v-model="passwords.current_password"
              type="password"
              class="input-base"
              :class="{ 'border-red-400': passwordErrors.current_password }"
            />
            <p v-if="passwordErrors.current_password" class="mt-1 text-xs text-red-500">{{ passwordErrors.current_password }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('author.profile.new_password') }}
            </label>
            <input
              v-model="passwords.new_password"
              type="password"
              class="input-base"
              :class="{ 'border-red-400': passwordErrors.new_password }"
            />
            <p v-if="passwordErrors.new_password" class="mt-1 text-xs text-red-500">{{ passwordErrors.new_password }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('author.profile.confirm_password') }}
            </label>
            <input
              v-model="passwords.confirm_password"
              type="password"
              class="input-base"
              :class="{ 'border-red-400': passwordErrors.confirm_password }"
            />
            <p v-if="passwordErrors.confirm_password" class="mt-1 text-xs text-red-500">{{ passwordErrors.confirm_password }}</p>
          </div>

          <div v-if="passwordSuccess" class="flex items-center gap-2 text-sm text-green-600 dark:text-green-400">
            <CheckCircle :size="16" />{{ t('author.profile.password_changed') }}
          </div>
          <div v-if="passwordError" class="flex items-center gap-2 text-sm text-red-500">
            <AlertCircle :size="16" />{{ passwordError }}
          </div>

          <button
            type="button"
            class="btn-primary"
            :disabled="passwordSaving"
            @click="changePassword"
          >
            <Loader2 v-if="passwordSaving" :size="16" class="animate-spin" />
            <KeyRound v-else :size="16" />
            {{ t('author.profile.change_password') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
