<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ChevronDown, ChevronUp } from 'lucide-vue-next'

const props = defineProps<{
  text: string
  maxLines?: number
}>()

const { t } = useI18n()
const expanded = ref(false)
const MAX_CHARS = 400
const isLong = props.text.length > MAX_CHARS
</script>

<template>
  <div>
    <p
      class="text-sm leading-relaxed text-slate-600 dark:text-slate-300"
      :class="{ 'line-clamp-3': !expanded && isLong }"
    >
      {{ text }}
    </p>
    <button
      v-if="isLong"
      class="mt-2 inline-flex items-center gap-1 text-xs font-medium text-primary-600 hover:underline dark:text-primary-400"
      @click="expanded = !expanded"
    >
      <template v-if="expanded">
        {{ t('article.show_less') }}
        <ChevronUp :size="14" />
      </template>
      <template v-else>
        {{ t('article.show_more') }}
        <ChevronDown :size="14" />
      </template>
    </button>
  </div>
</template>
