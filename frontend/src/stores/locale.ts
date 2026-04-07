import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

export type Locale = 'uz' | 'ru' | 'en'

export const useLocaleStore = defineStore('locale', () => {
  const current = ref<Locale>(
    (localStorage.getItem('locale') as Locale) || 'uz'
  )

  function setLocale(locale: Locale) {
    current.value = locale
    localStorage.setItem('locale', locale)
    document.documentElement.lang = locale
  }

  return { current, setLocale }
})
