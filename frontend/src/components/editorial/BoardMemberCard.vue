<script setup lang="ts">
import { computed } from 'vue'
import {
  BadgeCheck, Mail, Building2, MapPin, GraduationCap,
  Globe, BookOpen, Search as ScholarIcon,
} from 'lucide-vue-next'

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
  email?: string
  degree?: string
  specialization?: string
  scopus_id?: string
  researcher_id?: string
  google_scholar_url?: string
  website_url?: string
  order: number
  is_active: boolean
}

const props = defineProps<{
  member: EditorialMember
  size?: 'large' | 'medium' | 'small'
}>()

const initials = computed(() =>
  props.member.name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase()
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

const roleAccent = computed(() => {
  const map: Record<string, string> = {
    editor_in_chief: 'from-amber-400 to-amber-600',
    associate_editor: 'from-violet-400 to-violet-600',
    section_editor: 'from-blue-400 to-blue-600',
    reviewer: 'from-slate-400 to-slate-600',
  }
  return map[props.member.role] ?? 'from-primary-400 to-primary-600'
})

const isLarge = computed(() => props.size === 'large')

function resolvePhoto(u?: string) {
  if (!u) return ''
  return u.startsWith('http') || u.startsWith('/') ? u : `/api/uploads/${u}`
}
</script>

<template>
  <article
    class="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm transition hover:border-primary-400 hover:shadow-lg dark:border-slate-700 dark:bg-slate-800"
  >
    <!-- Accent bar -->
    <div class="h-1 bg-gradient-to-r" :class="roleAccent" />

    <div
      class="flex gap-5 p-5 sm:p-6"
      :class="isLarge ? 'flex-col sm:flex-row sm:items-start' : 'flex-col items-center text-center sm:flex-row sm:text-left sm:items-start'"
    >
      <!-- Avatar -->
      <div class="shrink-0">
        <div
          class="overflow-hidden rounded-full border-2 border-white shadow-md bg-gradient-to-br ring-1 ring-slate-200 dark:ring-slate-700"
          :class="[
            roleAccent,
            isLarge ? 'h-28 w-28' : size === 'small' ? 'h-16 w-16' : 'h-20 w-20',
          ]"
        >
          <img
            v-if="member.photo_url"
            :src="resolvePhoto(member.photo_url)"
            :alt="member.name"
            class="h-full w-full object-cover"
          />
          <div
            v-else
            class="flex h-full w-full items-center justify-center font-bold text-white"
            :class="isLarge ? 'text-2xl' : size === 'small' ? 'text-sm' : 'text-lg'"
          >
            {{ initials }}
          </div>
        </div>
      </div>

      <!-- Info -->
      <div class="min-w-0 flex-1">
        <!-- Role + title row -->
        <div class="flex flex-wrap items-center gap-2">
          <span
            class="inline-flex items-center gap-1 rounded-full bg-primary-50 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wide text-primary-700 dark:bg-primary-950/40 dark:text-primary-300"
          >
            <BadgeCheck :size="11" />{{ roleLabel }}
          </span>
          <span v-if="member.title" class="text-xs font-medium text-slate-500 dark:text-slate-400">
            {{ member.title }}
          </span>
        </div>

        <!-- Name -->
        <h3
          class="mt-2 font-serif font-bold text-journal-800 dark:text-primary-300"
          :class="isLarge ? 'text-2xl' : 'text-lg'"
        >
          {{ member.name }}
        </h3>

        <!-- Degree / specialization -->
        <p
          v-if="member.degree || member.specialization"
          class="mt-1 text-sm text-slate-600 dark:text-slate-300"
        >
          <span v-if="member.degree" class="font-semibold">{{ member.degree }}</span>
          <span v-if="member.degree && member.specialization"> · </span>
          <span v-if="member.specialization">{{ member.specialization }}</span>
        </p>

        <!-- Affiliation / country -->
        <div
          v-if="member.affiliation || member.country"
          class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-500 dark:text-slate-400"
        >
          <span v-if="member.affiliation" class="inline-flex items-center gap-1">
            <Building2 :size="13" />{{ member.affiliation }}
          </span>
          <span v-if="member.country" class="inline-flex items-center gap-1">
            <MapPin :size="13" />{{ member.country }}
          </span>
        </div>

        <!-- Bio (large only) -->
        <p
          v-if="isLarge && member.bio"
          class="mt-3 text-sm leading-relaxed text-slate-600 dark:text-slate-300"
        >
          {{ member.bio }}
        </p>

        <!-- Links row -->
        <div class="mt-3 flex flex-wrap items-center gap-2">
          <a
            v-if="member.email"
            :href="`mailto:${member.email}`"
            class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700 hover:bg-primary-50 hover:text-primary-700 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
          >
            <Mail :size="11" />Email
          </a>
          <a
            v-if="member.orcid_id"
            :href="`https://orcid.org/${member.orcid_id}`"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 rounded-md bg-[#a6ce39]/15 px-2 py-1 text-xs text-[#6fa01e] hover:bg-[#a6ce39]/25 dark:text-[#a6ce39]"
          >
            <GraduationCap :size="11" />ORCID
          </a>
          <a
            v-if="member.scopus_id"
            :href="`https://www.scopus.com/authid/detail.uri?authorId=${member.scopus_id}`"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 rounded-md bg-orange-50 px-2 py-1 text-xs text-orange-700 hover:bg-orange-100 dark:bg-orange-950/30 dark:text-orange-300"
          >
            <BookOpen :size="11" />Scopus
          </a>
          <a
            v-if="member.google_scholar_url"
            :href="member.google_scholar_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 rounded-md bg-blue-50 px-2 py-1 text-xs text-blue-700 hover:bg-blue-100 dark:bg-blue-950/30 dark:text-blue-300"
          >
            <ScholarIcon :size="11" />Scholar
          </a>
          <a
            v-if="member.website_url"
            :href="member.website_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-700 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300"
          >
            <Globe :size="11" />Website
          </a>
        </div>
      </div>
    </div>
  </article>
</template>
