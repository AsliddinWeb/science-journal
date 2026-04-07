<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { CheckCircle } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const authStore = useAuthStore()
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-slate-50 px-4 dark:bg-slate-950">
    <div class="w-full max-w-md">
      <div class="card p-10 text-center">
        <div class="mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl bg-green-100 dark:bg-green-950">
          <CheckCircle :size="32" class="text-green-500" />
        </div>
        <h1 class="font-serif text-2xl font-bold text-slate-900 dark:text-white">
          {{ t('author.verify.confirmed_title') }}
        </h1>
        <p class="mt-3 text-slate-500 dark:text-slate-400">
          {{ t('author.verify.confirmed_desc') }}
        </p>

        <div class="mt-8 flex flex-col gap-3 sm:flex-row sm:justify-center">
          <router-link
            v-if="authStore.isAuthenticated"
            :to="{ name: 'author-dashboard' }"
            class="btn-primary"
          >
            {{ t('author.dashboard.title') }}
          </router-link>
          <router-link v-else :to="{ name: 'login' }" class="btn-primary">
            {{ t('nav.login') }}
          </router-link>
          <router-link :to="{ name: 'home' }" class="btn-ghost">
            {{ t('errors.go_home') }}
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>
