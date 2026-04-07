<script setup lang="ts">
import { onMounted } from 'vue'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import AppToast from '@/components/ui/AppToast.vue'

const themeStore = useThemeStore()
const authStore = useAuthStore()

onMounted(async () => {
  themeStore.init()
  if (authStore.accessToken) {
    await authStore.fetchMe()
  }
})
</script>

<template>
  <RouterView />
  <AppToast />
</template>
