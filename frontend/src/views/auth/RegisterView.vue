<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BookOpen } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useSiteInfoStore } from '@/stores/siteInfo'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'

const { t } = useI18n()
const siteInfo = useSiteInfoStore()
const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const form = ref({ email: '', password: '', full_name: '', affiliation: '', country: '', orcid_id: '' })
const loading = ref(false)
const errors = ref<Record<string, string>>({})

async function handleSubmit() {
  errors.value = {}
  if (!form.value.full_name) { errors.value.full_name = 'Full name is required'; return }
  if (!form.value.email) { errors.value.email = 'Email is required'; return }
  if (form.value.password.length < 8) { errors.value.password = 'Password must be at least 8 characters'; return }

  loading.value = true
  try {
    await authStore.register(form.value)
    toast.success('Account created successfully! Welcome.')
    router.push('/author/dashboard')
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toast.error(msg || 'Registration failed. Please try again.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-4 py-12 dark:bg-slate-950">
    <div class="w-full max-w-md">
      <div class="mb-8 text-center">
        <RouterLink to="/" class="inline-flex items-center gap-2.5">
          <img
            v-if="siteInfo.logoUrl"
            :src="siteInfo.logoUrl"
            :alt="siteInfo.siteName"
            class="h-10 w-auto max-w-[120px] object-contain"
          />
          <div v-else class="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-600">
            <BookOpen :size="20" class="text-white" />
          </div>
          <span class="font-serif text-xl font-bold text-slate-900 dark:text-white">
            {{ siteInfo.siteName }}
          </span>
        </RouterLink>
      </div>

      <div class="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">{{ t('auth.register_title') }}</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ t('auth.have_account') }}
          <RouterLink to="/login" class="font-medium text-primary-600 hover:underline dark:text-primary-400">
            {{ t('auth.login_link') }}
          </RouterLink>
        </p>

        <form class="mt-6 flex flex-col gap-4" @submit.prevent="handleSubmit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.full_name') }} *
            </label>
            <input v-model="form.full_name" type="text" class="input-base" :class="errors.full_name ? 'border-red-500' : ''" />
            <p v-if="errors.full_name" class="mt-1 text-xs text-red-600">{{ errors.full_name }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.email') }} *
            </label>
            <input v-model="form.email" type="email" autocomplete="email" class="input-base" :class="errors.email ? 'border-red-500' : ''" />
            <p v-if="errors.email" class="mt-1 text-xs text-red-600">{{ errors.email }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.password') }} *
            </label>
            <input v-model="form.password" type="password" autocomplete="new-password" class="input-base" :class="errors.password ? 'border-red-500' : ''" />
            <p v-if="errors.password" class="mt-1 text-xs text-red-600">{{ errors.password }}</p>
          </div>

          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.affiliation') }}
            </label>
            <input v-model="form.affiliation" type="text" class="input-base" :placeholder="t('auth.affiliation')" />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('auth.country') }}
              </label>
              <input v-model="form.country" type="text" class="input-base" />
            </div>
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('auth.orcid') }}
              </label>
              <input v-model="form.orcid_id" type="text" class="input-base" placeholder="0000-0000-0000-0000" />
            </div>
          </div>

          <AppButton type="submit" :loading="loading" full-width class="mt-2">
            {{ t('auth.register_btn') }}
          </AppButton>
        </form>
      </div>
    </div>
  </div>
</template>
