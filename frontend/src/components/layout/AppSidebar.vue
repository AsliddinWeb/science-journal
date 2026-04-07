<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  LayoutDashboard, FileText, Users, BookOpen,
  UserCheck, FileEdit, X, BookMarked, Megaphone,
  Database, Tag, Presentation, Home,
} from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'

defineEmits<{ close: [] }>()

const { t } = useI18n()
const route = useRoute()

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
      { to: '/admin/articles', icon: FileText, label: t('admin.sidebar.articles') },
      { to: '/admin/volumes', icon: BookOpen, label: t('admin.sidebar.volumes') },
      { to: '/admin/conferences', icon: Presentation, label: t('admin.sidebar.conferences') },
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
      { to: '/admin/categories', icon: Tag, label: t('admin.sidebar.categories') },
      { to: '/admin/indexing', icon: Database, label: t('admin.sidebar.indexing') },
    ],
  },
])

const isActive = (path: string) => route.path.startsWith(path)
</script>

<template>
  <div class="flex h-full flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900">
    <!-- Logo -->
    <div class="flex h-16 items-center justify-between gap-3 border-b border-slate-200 px-5 dark:border-slate-800">
      <RouterLink to="/" class="flex items-center gap-2.5" @click="$emit('close')">
        <div class="flex h-7 w-7 items-center justify-center rounded-lg bg-primary-600">
          <BookMarked :size="14" class="text-white" />
        </div>
        <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ t('admin.panel_title') }}</span>
      </RouterLink>
      <button
        class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 lg:hidden"
        @click="$emit('close')"
      >
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
              :class="
                isActive(item.to)
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                  : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
              "
              @click="$emit('close')"
            >
              <component :is="item.icon" :size="17" />
              {{ item.label }}
            </RouterLink>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Bottom -->
    <div class="border-t border-slate-200 p-3 dark:border-slate-800">
      <RouterLink
        to="/"
        class="flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
        @click="$emit('close')"
      >
        {{ t('admin.view_site') }}
      </RouterLink>
    </div>
  </div>
</template>
