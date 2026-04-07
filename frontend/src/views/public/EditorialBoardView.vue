<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { Users, AlertCircle, RefreshCw } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import BoardMemberCard from '@/components/editorial/BoardMemberCard.vue'
import type { EditorialMember } from '@/components/editorial/BoardMemberCard.vue'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()

useSeoMeta({
  title: t('nav.editorial'),
  description: 'Meet the distinguished editorial board members of Science and Innovation Journal.',
  canonical: 'https://scientists.uz/editorial-board',
  ogUrl: 'https://scientists.uz/editorial-board',
})
const members = ref<EditorialMember[]>([])
const loading = ref(true)
const error = ref(false)

async function load() {
  loading.value = true
  error.value = false
  try {
    members.value = await api.get<EditorialMember[]>('/api/editorial')
  } catch {
    error.value = true
  } finally {
    loading.value = false
  }
}

onMounted(load)

const editorInChief = computed(() =>
  members.value.filter((m) => m.role === 'editor_in_chief' && m.is_active)
)
const associateEditors = computed(() =>
  members.value.filter((m) => m.role === 'associate_editor' && m.is_active).sort((a, b) => a.order - b.order)
)
const sectionEditors = computed(() =>
  members.value.filter((m) => m.role === 'section_editor' && m.is_active).sort((a, b) => a.order - b.order)
)
const reviewers = computed(() =>
  members.value.filter((m) => m.role === 'reviewer' && m.is_active).sort((a, b) => a.order - b.order)
)
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <div class="flex items-center gap-4">
        <div class="flex h-12 w-12 items-center justify-center rounded-xl bg-white/10 backdrop-blur">
          <Users :size="24" class="text-primary-300" />
        </div>
        <div>
          <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('editorial.title') }}</h1>
          <p class="mt-1 text-sm text-slate-300">{{ t('editorial.subtitle') }}</p>
        </div>
      </div>
    </section>

    <div>

      <!-- Error -->
      <div v-if="error" class="flex flex-col items-center py-20">
        <AlertCircle :size="40" class="text-red-400" />
        <p class="mt-3 font-semibold text-red-700 dark:text-red-400">{{ t('common.error') }}</p>
        <button class="btn-ghost mt-4" @click="load"><RefreshCw :size="15" />{{ t('common.retry') }}</button>
      </div>

      <!-- Skeleton -->
      <div v-else-if="loading" class="space-y-10">
        <div class="card animate-pulse p-6">
          <div class="flex gap-5">
            <div class="h-24 w-24 rounded-full bg-slate-200 dark:bg-slate-700 shrink-0" />
            <div class="flex-1 space-y-3 pt-2">
              <div class="h-3 w-24 rounded bg-slate-200 dark:bg-slate-700" />
              <div class="h-6 w-48 rounded bg-slate-200 dark:bg-slate-700" />
              <div class="h-4 w-32 rounded bg-slate-100 dark:bg-slate-800" />
            </div>
          </div>
        </div>
        <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div v-for="i in 4" :key="i" class="card animate-pulse p-5">
            <div class="flex gap-3">
              <div class="h-14 w-14 rounded-full bg-slate-200 dark:bg-slate-700 shrink-0" />
              <div class="flex-1 space-y-2 pt-1">
                <div class="h-4 w-32 rounded bg-slate-200 dark:bg-slate-700" />
                <div class="h-3 w-24 rounded bg-slate-100 dark:bg-slate-800" />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="space-y-14">

        <!-- Editor-in-Chief -->
        <section v-if="editorInChief.length">
          <h2 class="mb-5 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
            {{ t('editorial.editor_in_chief') }}
          </h2>
          <BoardMemberCard
            v-for="m in editorInChief"
            :key="m.id"
            :member="m"
            size="large"
          />
        </section>

        <!-- Associate Editors -->
        <section v-if="associateEditors.length">
          <h2 class="mb-5 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
            {{ t('editorial.associate_editors') }}
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <BoardMemberCard
              v-for="m in associateEditors"
              :key="m.id"
              :member="m"
              size="medium"
            />
          </div>
        </section>

        <!-- Section Editors -->
        <section v-if="sectionEditors.length">
          <h2 class="mb-5 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
            {{ t('editorial.section_editors') }}
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <BoardMemberCard
              v-for="m in sectionEditors"
              :key="m.id"
              :member="m"
              size="small"
            />
          </div>
        </section>

        <!-- Reviewers -->
        <section v-if="reviewers.length">
          <h2 class="mb-5 font-serif text-xl font-bold text-journal-800 dark:text-primary-300">
            {{ t('editorial.reviewers') }}
          </h2>
          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <BoardMemberCard
              v-for="m in reviewers"
              :key="m.id"
              :member="m"
              size="small"
            />
          </div>
        </section>

        <!-- Empty state -->
        <div v-if="!loading && members.length === 0" class="flex flex-col items-center py-20">
          <Users :size="48" class="text-slate-200 dark:text-slate-700" />
          <p class="mt-4 text-slate-400">{{ t('editorial.no_members') }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
