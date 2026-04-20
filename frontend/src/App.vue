<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useSiteThemeStore } from '@/stores/siteTheme'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/composables/useApi'
import AppToast from '@/components/ui/AppToast.vue'

const themeStore = useThemeStore()
const siteTheme = useSiteThemeStore()
const authStore = useAuthStore()

// Apply persisted theme synchronously (before paint) to avoid flash
siteTheme.init()

onMounted(async () => {
  themeStore.init()
  if (authStore.accessToken) {
    await authStore.fetchMe()
  }
  // Pull the server-side default; localStorage still wins if user picked one.
  try {
    const hs = await api.get<{ theme?: string }>('/api/home-settings')
    if (hs?.theme && !localStorage.getItem('site-theme')) {
      siteTheme.set(hs.theme)
    }
  } catch { /* silent — default theme stays */ }
})
</script>

<template>
  <RouterView />
  <AppToast />
</template>
