import { createI18n } from 'vue-i18n'
import uz from './locales/uz.json'
import ru from './locales/ru.json'
import en from './locales/en.json'

type MessageSchema = typeof en

const savedLocale = localStorage.getItem('locale') || 'uz'

const i18n = createI18n<[MessageSchema], 'uz' | 'ru' | 'en'>({
  legacy: false,
  locale: savedLocale as 'uz' | 'ru' | 'en',
  fallbackLocale: 'en',
  messages: {
    uz,
    ru,
    en,
  },
})

export default i18n
