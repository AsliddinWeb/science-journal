<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

type ArticleStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'revision_required'
  | 'accepted'
  | 'rejected'
  | 'published'

interface Props {
  status: ArticleStatus
  size?: 'sm' | 'md'
}

const props = withDefaults(defineProps<Props>(), { size: 'md' })
const { t } = useI18n()

const config = computed(() => {
  const map: Record<ArticleStatus, { label: string; classes: string }> = {
    draft: {
      label: t('author.status.draft'),
      classes: 'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400',
    },
    submitted: {
      label: t('author.status.submitted'),
      classes: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-400',
    },
    under_review: {
      label: t('author.status.under_review'),
      classes: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-400',
    },
    revision_required: {
      label: t('author.status.revision_required'),
      classes: 'bg-orange-100 text-orange-700 dark:bg-orange-950 dark:text-orange-400',
    },
    accepted: {
      label: t('author.status.accepted'),
      classes: 'bg-green-100 text-green-700 dark:bg-green-950 dark:text-green-400',
    },
    rejected: {
      label: t('author.status.rejected'),
      classes: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-400',
    },
    published: {
      label: t('author.status.published'),
      classes: 'bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-400',
    },
  }
  return map[props.status] ?? map.draft
})
</script>

<template>
  <span
    :class="[
      'inline-flex items-center rounded-full font-medium',
      size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs',
      config.classes,
    ]"
  >
    {{ config.label }}
  </span>
</template>
