<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { BookOpen } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useSiteInfoStore } from '@/stores/siteInfo'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'

const { t } = useI18n()
const siteInfo = useSiteInfoStore()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const toast = useToast()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errors = ref<Record<string, string>>({})

async function handleSubmit() {
  errors.value = {}
  if (!email.value) { errors.value.email = 'Email is required'; return }
  if (!password.value) { errors.value.password = 'Password is required'; return }

  loading.value = true
  try {
    await authStore.login({ email: email.value, password: password.value })
    const redirect = (route.query.redirect as string) || '/author/dashboard'
    router.push(redirect)
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toast.error(msg || 'Invalid email or password')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
    <div class="w-full max-w-md">
      <!-- Logo -->
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
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">{{ t('auth.login_title') }}</h1>
        <p class="mt-1 text-sm text-slate-500 dark:text-slate-400">
          {{ t('auth.no_account') }}
          <RouterLink to="/register" class="font-medium text-primary-600 hover:underline dark:text-primary-400">
            {{ t('auth.register_link') }}
          </RouterLink>
        </p>

        <form class="mt-6 flex flex-col gap-4" @submit.prevent="handleSubmit">
          <div>
            <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
              {{ t('auth.email') }}
            </label>
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              class="input-base"
              :class="errors.email ? 'border-red-500 focus:ring-red-500' : ''"
              :placeholder="t('auth.email')"
            />
            <p v-if="errors.email" class="mt-1 text-xs text-red-600">{{ errors.email }}</p>
          </div>

          <div>
            <div class="mb-1.5 flex items-center justify-between">
              <label class="text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('auth.password') }}
              </label>
              <RouterLink to="/forgot-password" class="text-xs text-primary-600 hover:underline dark:text-primary-400">
                {{ t('auth.forgot_password') }}
              </RouterLink>
            </div>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              class="input-base"
              :class="errors.password ? 'border-red-500 focus:ring-red-500' : ''"
              :placeholder="t('auth.password')"
            />
            <p v-if="errors.password" class="mt-1 text-xs text-red-600">{{ errors.password }}</p>
          </div>

          <AppButton type="submit" :loading="loading" full-width class="mt-2">
            {{ t('auth.login_btn') }}
          </AppButton>
        </form>
      </div>
    </div>
  </div>
</template>
