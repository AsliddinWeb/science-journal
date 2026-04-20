<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  LayoutDashboard, FileText, Users,
  UserCheck, FileEdit, X, BookMarked, Megaphone,
  Database, Presentation, Home, ChevronDown,
} from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

defineEmits<{ close: [] }>()

const { t } = useI18n()
const route = useRoute()
const confOpen = ref(false)
const articlesOpen = ref(false)

interface NavGroup {
  label: string
  items: { to: string; icon: object; label: string }[]
}

const navGroups = computed<NavGroup[]>(() => [
  {
    label: t('admin.sidebar.overview'),
    items: [
      { to: '/admin/dashboard', icon: LayoutDashboard, label: t('admin.sidebar.dashboard') },
    ],
  },
  {
    label: t('admin.sidebar.content'),
    items: [
      { to: '/admin/pages', icon: FileEdit, label: t('admin.sidebar.pages') },
    ],
  },
  {
    label: t('admin.sidebar.community'),
    items: [
      { to: '/admin/users', icon: Users, label: t('admin.sidebar.users') },
      { to: '/admin/editorial', icon: UserCheck, label: t('admin.sidebar.editorial') },
      { to: '/admin/announcements', icon: Megaphone, label: t('admin.sidebar.announcements') },
    ],
  },
  {
    label: t('admin.sidebar.settings'),
    items: [
      { to: '/admin/home-settings', icon: Home, label: t('admin.sidebar.homeSettings') },
      { to: '/admin/indexing', icon: Database, label: t('admin.sidebar.indexing') },
    ],
  },
])

const confLinks = computed(() => [
  { to: '/admin/conf/list', label: t('admin.sidebar.conferences') },
  { to: '/admin/conf/sessions', label: t('admin.conferences.sessions') },
  { to: '/admin/conferences', label: t('admin.conferences.view_papers') },
])

const articleLinks = computed(() => [
  { to: '/admin/articles', label: t('admin.sidebar.articles') },
  { to: '/admin/volumes', label: t('admin.sidebar.volumes') },
  { to: '/admin/categories', label: t('admin.sidebar.categories') },
])

const isActive = (path: string) => route.path.startsWith(path)
const isConfActive = computed(() => route.path.startsWith('/admin/conf'))
const isArticlesActive = computed(() =>
  route.path.startsWith('/admin/articles') ||
  route.path.startsWith('/admin/volumes') ||
  route.path.startsWith('/admin/categories')
)
</script>

<template>
  <div class="flex h-full flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
    <!-- Logo -->
    <div class="flex h-16 items-center justify-between gap-3 border-b border-slate-200 px-5 dark:border-slate-800">
      <RouterLink to="/admin/dashboard" class="flex items-center gap-2.5" @click="$emit('close')">
        <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-primary-600">
          <BookMarked :size="14" class="text-white" />
        </div>
        <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ t('admin.panel_title') }}</span>
      </RouterLink>
      <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden" @click="$emit('close')">
        <X :size="16" />
      </button>
    </div>

    <!-- Nav -->
    <nav class="flex-1 overflow-y-auto p-3">
      <div v-for="group in navGroups" :key="group.label" class="mb-4">
        <p class="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-slate-400">
          {{ group.label }}
        </p>
        <ul class="flex flex-col gap-0.5">
          <li v-for="item in group.items" :key="item.to">
            <RouterLink
              :to="item.to"
              class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
              :class="isActive(item.to) ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'"
              @click="$emit('close')"
            >
              <component :is="item.icon" :size="17" />
              {{ item.label }}
            </RouterLink>
          </li>

          <!-- Articles dropdown — in content group -->
          <li v-if="group.label === t('admin.sidebar.content')">
            <button
              class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
              :class="isArticlesActive || articlesOpen ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'"
              @click="articlesOpen = !articlesOpen"
            >
              <span class="flex items-center gap-3">
                <FileText :size="17" />
                {{ t('admin.sidebar.articles') }}
              </span>
              <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': articlesOpen }" />
            </button>
            <ul v-if="articlesOpen || isArticlesActive" class="ml-8 mt-0.5 flex flex-col gap-0.5 border-l-2 border-slate-200 pl-3 dark:border-slate-700">
              <li v-for="link in articleLinks" :key="link.to">
                <RouterLink
                  :to="link.to"
                  class="block rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
                  :class="route.path === link.to ? 'text-primary-700 dark:text-primary-300' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'"
                  @click="$emit('close')"
                >
                  {{ link.label }}
                </RouterLink>
              </li>
            </ul>
          </li>

          <!-- Conferences dropdown — after content group -->
          <li v-if="group.label === t('admin.sidebar.content')">
            <button
              class="flex w-full items-center justify-between rounded-lg px-3 py-2.5 text-sm font-medium transition-colors"
              :class="isConfActive || confOpen ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'"
              @click="confOpen = !confOpen"
            >
              <span class="flex items-center gap-3">
                <Presentation :size="17" />
                {{ t('admin.sidebar.conferences') }}
              </span>
              <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': confOpen }" />
            </button>
            <ul v-if="confOpen || isConfActive" class="ml-8 mt-0.5 flex flex-col gap-0.5 border-l-2 border-slate-200 pl-3 dark:border-slate-700">
              <li v-for="link in confLinks" :key="link.to">
                <RouterLink
                  :to="link.to"
                  class="block rounded-md px-2 py-1.5 text-xs font-medium transition-colors"
                  :class="route.path === link.to ? 'text-primary-700 dark:text-primary-300' : 'text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200'"
                  @click="$emit('close')"
                >
                  {{ link.label }}
                </RouterLink>
              </li>
            </ul>
          </li>
        </ul>
      </div>
    </nav>

  </div>
</template>
