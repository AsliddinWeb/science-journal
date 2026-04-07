<script setup lang="ts">
import { ExternalLink } from 'lucide-vue-next'
import type { ArticleAuthor } from '@/types/article'
import type { UserPublic } from '@/types/user'

defineProps<{
  authors: ArticleAuthor[]
  mainAuthor?: UserPublic
  compact?: boolean
}>()

function getAuthorName(author: ArticleAuthor): string {
  if (author.user) return author.user.full_name
  if (author.guest_name) return author.guest_name
  return 'Unknown Author'
}

function getAuthorOrcid(author: ArticleAuthor): string | undefined {
  return author.user?.orcid_id ?? author.guest_orcid
}
</script>

<template>
  <div>
    <!-- Compact mode: comma-separated inline -->
    <span v-if="compact" class="text-sm text-slate-600 dark:text-slate-400">
      <span v-if="mainAuthor">{{ mainAuthor.full_name }}</span>
      <template v-if="authors.length">
        <span v-if="mainAuthor">, </span>
        <span v-for="(author, idx) in authors" :key="author.id">
          {{ getAuthorName(author) }}<span v-if="idx < authors.length - 1">, </span>
        </span>
      </template>
    </span>

    <!-- Full mode: list with affiliations + ORCID -->
    <ul v-else class="flex flex-col gap-3">
      <!-- Main author -->
      <li v-if="mainAuthor" class="flex items-start gap-2">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-100 text-xs font-semibold text-primary-700 dark:bg-primary-950 dark:text-primary-300">
          {{ mainAuthor.full_name.charAt(0).toUpperCase() }}
        </div>
        <div>
          <p class="text-sm font-medium text-slate-900 dark:text-white">
            {{ mainAuthor.full_name }}
            <span class="ml-1 text-xs text-primary-600 dark:text-primary-400">(Corresponding)</span>
          </p>
          <p v-if="mainAuthor.affiliation" class="text-xs text-slate-500 dark:text-slate-400">
            {{ mainAuthor.affiliation }}
            <span v-if="mainAuthor.country"> · {{ mainAuthor.country }}</span>
          </p>
          <a
            v-if="mainAuthor.orcid_id"
            :href="`https://orcid.org/${mainAuthor.orcid_id}`"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-0.5 inline-flex items-center gap-1 text-xs text-green-600 hover:underline dark:text-green-400"
          >
            <ExternalLink :size="10" />
            ORCID: {{ mainAuthor.orcid_id }}
          </a>
        </div>
      </li>

      <!-- Co-authors -->
      <li v-for="author in authors" :key="author.id" class="flex items-start gap-2">
        <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600 dark:bg-slate-700 dark:text-slate-300">
          {{ getAuthorName(author).charAt(0).toUpperCase() }}
        </div>
        <div>
          <p class="text-sm font-medium text-slate-900 dark:text-white">{{ getAuthorName(author) }}</p>
          <p v-if="author.user?.affiliation ?? author.guest_affiliation" class="text-xs text-slate-500 dark:text-slate-400">
            {{ author.user?.affiliation ?? author.guest_affiliation }}
          </p>
          <a
            v-if="getAuthorOrcid(author)"
            :href="`https://orcid.org/${getAuthorOrcid(author)}`"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-0.5 inline-flex items-center gap-1 text-xs text-green-600 hover:underline dark:text-green-400"
          >
            <ExternalLink :size="10" />
            ORCID: {{ getAuthorOrcid(author) }}
          </a>
        </div>
      </li>
    </ul>
  </div>
</template>
