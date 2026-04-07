<script setup lang="ts">
import { computed } from 'vue'
import { ExternalLink } from 'lucide-vue-next'

export interface EditorialMember {
  id: string
  name: string
  title?: string
  affiliation?: string
  country?: string
  role: 'editor_in_chief' | 'associate_editor' | 'section_editor' | 'reviewer'
  photo_url?: string
  bio?: string
  orcid_id?: string
  order: number
  is_active: boolean
}

const props = defineProps<{
  member: EditorialMember
  size?: 'large' | 'medium' | 'small'
}>()

const initials = computed(() =>
  props.member.name
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
)

const roleLabel = computed(() => {
  const map: Record<string, string> = {
    editor_in_chief: 'Editor-in-Chief',
    associate_editor: 'Associate Editor',
    section_editor: 'Section Editor',
    reviewer: 'Reviewer',
  }
  return map[props.member.role] ?? props.member.role
})

const avatarSize = computed(() => {
  if (props.size === 'large') return 'h-24 w-24 text-2xl'
  if (props.size === 'small') return 'h-12 w-12 text-base'
  return 'h-16 w-16 text-lg'
})
</script>

<template>
  <div
    class="card flex gap-4 p-5 transition-shadow hover:shadow-md"
    :class="size === 'large' ? 'sm:flex-row items-start' : 'flex-col items-center text-center sm:flex-row sm:text-left sm:items-start'"
  >
    <!-- Avatar -->
    <div :class="['shrink-0 flex items-center justify-center rounded-full overflow-hidden bg-primary-100 dark:bg-primary-950 font-bold text-primary-700 dark:text-primary-300', avatarSize]">
      <img
        v-if="member.photo_url"
        :src="member.photo_url"
        :alt="member.name"
        class="h-full w-full object-cover"
      />
      <span v-else>{{ initials }}</span>
    </div>

    <!-- Info -->
    <div class="min-w-0 flex-1">
      <p class="text-xs font-semibold uppercase tracking-wide text-primary-600 dark:text-primary-400">
        {{ roleLabel }}
      </p>
      <h3 class="mt-0.5 font-serif font-semibold text-slate-900 dark:text-white"
        :class="size === 'large' ? 'text-xl' : 'text-base'">
        {{ member.name }}
      </h3>
      <p v-if="member.title" class="mt-0.5 text-xs font-medium text-slate-600 dark:text-slate-300">
        {{ member.title }}
      </p>
      <p v-if="member.affiliation" class="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
        {{ member.affiliation }}
        <span v-if="member.country"> · {{ member.country }}</span>
      </p>
      <p v-if="size === 'large' && member.bio" class="mt-2 text-sm text-slate-600 dark:text-slate-400 line-clamp-3">
        {{ member.bio }}
      </p>
      <a
        v-if="member.orcid_id"
        :href="`https://orcid.org/${member.orcid_id}`"
        target="_blank"
        rel="noopener noreferrer"
        class="mt-1.5 inline-flex items-center gap-1 text-xs text-green-600 hover:underline dark:text-green-400"
      >
        <ExternalLink :size="10" />
        ORCID
      </a>
    </div>
  </div>
</template>
