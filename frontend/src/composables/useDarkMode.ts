import { useThemeStore } from '@/stores/theme'
import { computed } from 'vue'

export function useDarkMode() {
  const themeStore = useThemeStore()

  const isDark = computed(() => themeStore.isDark)

  function toggle() {
    themeStore.toggle()
  }

  return { isDark, toggle }
}
