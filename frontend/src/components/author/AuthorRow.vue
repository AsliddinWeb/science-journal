<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { GripVertical, Trash2, ExternalLink } from 'lucide-vue-next'

export interface AuthorEntry {
  id: string  // local UUID for v-key
  user_id?: string | null
  name: string
  email?: string | null
  affiliation?: string | null
  country?: string | null
  orcid?: string | null
  is_corresponding: boolean
  readonly?: boolean
}

interface Props {
  author: AuthorEntry
  index: number
  canRemove?: boolean
}

const props = withDefaults(defineProps<Props>(), { canRemove: true })
const emit = defineEmits<{
  remove: [id: string]
  toggleCorresponding: [id: string]
}>()

const { t } = useI18n()

const initials = computed(() =>
  props.author.name
    .trim()
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('')
)
</script>

<template>
  <div
    class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-900"
  >
    <!-- Drag handle (visible only when parent has drag context) -->
    <div class="shrink-0 cursor-grab text-slate-300 hover:text-slate-500 dark:text-slate-700 dark:hover:text-slate-500 active:cursor-grabbing">
      <GripVertical :size="18" />
    </div>

    <!-- Order badge -->
    <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-400">
      {{ index + 1 }}
    </div>

    <!-- Avatar initials -->
    <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300">
      {{ initials }}
    </div>

    <!-- Info -->
    <div class="min-w-0 flex-1">
      <div class="flex items-center gap-2">
        <p class="truncate text-sm font-semibold text-slate-900 dark:text-white">{{ author.name }}</p>
        <span v-if="author.readonly" class="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-slate-500 dark:bg-slate-800">
          {{ t('author.submit.submitting_author') }}
        </span>
      </div>
      <p v-if="author.affiliation" class="truncate text-xs text-slate-500 dark:text-slate-400">
        {{ author.affiliation }}{{ author.country ? ` · ${author.country}` : '' }}
      </p>
    </div>

    <!-- Corresponding author toggle -->
    <label class="flex shrink-0 cursor-pointer items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
      <input
        type="checkbox"
        class="h-3.5 w-3.5 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
        :checked="author.is_corresponding"
        :disabled="author.readonly"
        @change="!author.readonly && $emit('toggleCorresponding', author.id)"
      />
      {{ t('author.submit.corresponding') }}
    </label>

    <!-- ORCID link -->
    <a
      v-if="author.orcid"
      :href="`https://orcid.org/${author.orcid}`"
      target="_blank"
      rel="noopener noreferrer"
      class="shrink-0 text-slate-400 hover:text-primary-600 dark:hover:text-primary-400"
    >
      <ExternalLink :size="14" />
    </a>

    <!-- Remove button -->
    <button
      v-if="canRemove && !author.readonly"
      type="button"
      class="shrink-0 rounded-lg p-1.5 text-slate-400 hover:bg-red-50 hover:text-red-500 dark:hover:bg-red-950/20"
      @click="$emit('remove', author.id)"
    >
      <Trash2 :size="15" />
    </button>
  </div>
</template>
