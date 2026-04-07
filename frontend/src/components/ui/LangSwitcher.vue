<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocaleStore, type Locale } from '@/stores/locale'
import { ChevronDown } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  variant?: 'navbar' | 'admin'
}>(), { variant: 'navbar' })

const { locale } = useI18n()
const localeStore = useLocaleStore()
const open = ref(false)

const languages = [
  { code: 'uz' as Locale, label: "O'zbek", short: 'UZ' },
  { code: 'ru' as Locale, label: 'Русский', short: 'RU' },
  { code: 'en' as Locale, label: 'English', short: 'EN' },
]

function select(code: Locale) {
  locale.value = code
  localeStore.setLocale(code)
  document.documentElement.lang = code
  open.value = false
}

const current = computed(() => languages.find((l) => l.code === localeStore.current) ?? languages[0])
</script>

<template>
  <div class="relative">
    <button
      class="flex items-center gap-1 rounded-lg px-2 py-2 text-sm font-medium transition"
      :class="variant === 'navbar'
        ? 'text-primary-300/80 hover:bg-white/10 hover:text-primary-200'
        : 'text-slate-500 hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200'"
      @click="open = !open"
    >
      <span>{{ current.short }}</span>
      <ChevronDown :size="14" />
    </button>

    <Transition
      enter-active-class="transition-all duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      leave-active-class="transition-all duration-100 ease-in"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="open"
        class="absolute right-0 top-full mt-1 w-36 rounded-xl border border-slate-200 bg-white p-1 shadow-lg dark:border-slate-700 dark:bg-slate-800"
      >
        <button
          v-for="lang in languages"
          :key="lang.code"
          class="flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm transition-colors"
          :class="
            localeStore.current === lang.code
              ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
              : 'text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700'
          "
          @click="select(lang.code)"
        >
          <span>{{ lang.label }}</span>
          <span class="text-xs text-slate-400">{{ lang.short }}</span>
        </button>
      </div>
    </Transition>
  </div>
</template>
