import { defineStore } from 'pinia'
import { ref } from 'vue'
import { THEMES, DEFAULT_THEME_ID, findTheme, applyTheme } from '@/theme/themes'

const LS_KEY = 'site-theme'

export const useSiteThemeStore = defineStore('siteTheme', () => {
  const currentId = ref<string>(DEFAULT_THEME_ID)

  function set(id: string) {
    const theme = findTheme(id)
    applyTheme(theme)
    currentId.value = theme.id
    try { localStorage.setItem(LS_KEY, theme.id) } catch { /* ignore */ }
  }

  /**
   * Bootstrap. Applies, in order of preference:
   *   1. Value already in localStorage (user-chosen or previously fetched)
   *   2. Provided remote default (from /api/home-settings)
   *   3. DEFAULT_THEME_ID
   */
  function init(remoteDefault?: string | null) {
    let id: string | null = null
    try { id = localStorage.getItem(LS_KEY) } catch { /* ignore */ }
    set(id || remoteDefault || DEFAULT_THEME_ID)
  }

  return { currentId, set, init, themes: THEMES }
})
