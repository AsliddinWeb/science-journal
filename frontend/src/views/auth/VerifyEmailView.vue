<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Mail, RefreshCw, CheckCircle, AlertCircle, Loader2 } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const token = route.query.token as string | undefined
const resending = ref(false)
const resendSuccess = ref(false)
const resendError = ref('')

// If there's a token in the URL, verify automatically on mount
const verifying = ref(!!token)
const verifyError = ref('')

onMounted(async () => {
  if (!token) return
  try {
    await api.get(`/api/auth/verify-email?token=${encodeURIComponent(token)}`)
    router.replace({ name: 'email-confirmed' })
  } catch (e: any) {
    verifyError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    verifying.value = false
  }
})

async function resendVerification() {
  resending.value = true
  resendSuccess.value = false
  resendError.value = ''
  try {
    await api.post('/api/auth/resend-verification', {})
    resendSuccess.value = true
  } catch (e: any) {
    resendError.value = e?.response?.data?.detail ?? t('common.error')
  } finally {
    resending.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
    <div class="w-full max-w-md text-center">

      <!-- Verifying spinner -->
      <div v-if="verifying" class="flex flex-col items-center gap-4">
        <Loader2 :size="48" class="animate-spin text-primary-600" />
        <p class="text-slate-600 dark:text-slate-400">{{ t('author.verify.verifying') }}</p>
      </div>

      <!-- Verify error -->
      <div v-else-if="verifyError" class="card p-8">
        <AlertCircle :size="48" class="mx-auto text-red-400" />
        <h1 class="mt-4 font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('author.verify.error_title') }}
        </h1>
        <p class="mt-2 text-slate-500 dark:text-slate-400">{{ verifyError }}</p>
        <button class="btn-primary mt-6" @click="resendVerification" :disabled="resending">
          <Loader2 v-if="resending" :size="16" class="animate-spin" />
          <RefreshCw v-else :size="16" />
          {{ t('author.verify.resend') }}
        </button>
      </div>

      <!-- Default: no token — waiting for user to check email -->
      <div v-else class="card p-8">
        <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-primary-100 dark:bg-primary-950">
          <Mail :size="30" class="text-primary-600 dark:text-primary-400" />
        </div>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('author.verify.title') }}
        </h1>
        <p class="mt-3 text-slate-500 dark:text-slate-400">
          {{ t('author.verify.subtitle') }}
        </p>
        <p class="mt-2 text-sm text-slate-400">
          {{ t('author.verify.hint') }}
        </p>

        <!-- Resend section -->
        <div class="mt-6 rounded-xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-900">
          <p class="text-sm text-slate-600 dark:text-slate-400">{{ t('author.verify.no_email') }}</p>

          <div v-if="resendSuccess" class="mt-3 flex items-center justify-center gap-2 text-sm text-green-600 dark:text-green-400">
            <CheckCircle :size="16" />
            {{ t('author.verify.resend_success') }}
          </div>

          <div v-else-if="resendError" class="mt-2 text-xs text-red-500">{{ resendError }}</div>

          <button
            v-if="authStore.isAuthenticated"
            class="btn-ghost mt-3 text-sm"
            :disabled="resending || resendSuccess"
            @click="resendVerification"
          >
            <Loader2 v-if="resending" :size="14" class="animate-spin" />
            <RefreshCw v-else :size="14" />
            {{ t('author.verify.resend') }}
          </button>

          <p v-else class="mt-3 text-xs text-slate-400">
            {{ t('author.verify.login_to_resend') }}
            <router-link :to="{ name: 'login' }" class="text-primary-600 hover:underline">
              {{ t('nav.login') }}
            </router-link>
          </p>
        </div>

        <router-link :to="{ name: 'home' }" class="mt-6 block text-sm text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
          ← {{ t('errors.go_home') }}
        </router-link>
      </div>

    </div>
  </div>
</template>
