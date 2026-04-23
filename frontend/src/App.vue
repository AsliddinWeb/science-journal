<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useSiteThemeStore } from '@/stores/siteTheme'
import { useSiteInfoStore } from '@/stores/siteInfo'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/composables/useApi'
import AppToast from '@/components/ui/AppToast.vue'

const themeStore = useThemeStore()
const siteTheme = useSiteThemeStore()
const siteInfo = useSiteInfoStore()
const authStore = useAuthStore()

// Apply persisted theme synchronously (before paint) to avoid flash
siteTheme.init()

onMounted(async () => {
  themeStore.init()
  if (authStore.accessToken) {
    await authStore.fetchMe()
  }
  // Load site branding + theme in one go
  await siteInfo.load()
  const theme = (siteInfo.data as { theme?: string } | null)?.theme
  if (theme && !localStorage.getItem('site-theme')) siteTheme.set(theme)
})
</script>

<template>
  <RouterView />
  <AppToast />
</template>
