<script setup lang="ts">
import { onMounted, watch } from 'vue'
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

// Keep <link rel="icon"> in sync with the admin-uploaded logo, so the browser
// tab favicon matches the site brand. Falls back to the static /favicon.* set
// in index.html when no logo is configured.
function applyFavicon(url: string) {
  const mime =
    url.endsWith('.svg') ? 'image/svg+xml' :
    url.endsWith('.png') ? 'image/png' :
    url.endsWith('.jpg') || url.endsWith('.jpeg') ? 'image/jpeg' :
    url.endsWith('.ico') ? 'image/x-icon' :
    url.endsWith('.webp') ? 'image/webp' : ''
  document.querySelectorAll('link[rel~="icon"], link[rel="apple-touch-icon"]').forEach(el => el.remove())
  const icon = document.createElement('link')
  icon.rel = 'icon'
  if (mime) icon.type = mime
  icon.href = url
  document.head.appendChild(icon)
  const apple = document.createElement('link')
  apple.rel = 'apple-touch-icon'
  apple.href = url
  document.head.appendChild(apple)
}

watch(() => siteInfo.logoUrl, (url) => {
  if (url) applyFavicon(url)
})

onMounted(async () => {
  themeStore.init()
  if (authStore.accessToken) {
    await authStore.fetchMe()
  }
  // Load site branding + theme in one go
  await siteInfo.load()
  const theme = (siteInfo.data as { theme?: string } | null)?.theme
  if (theme && !localStorage.getItem('site-theme')) siteTheme.set(theme)
  if (siteInfo.logoUrl) applyFavicon(siteInfo.logoUrl)
})
</script>

<template>
  <RouterView />
  <AppToast />
</template>
