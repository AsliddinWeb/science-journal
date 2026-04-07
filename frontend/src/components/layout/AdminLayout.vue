<script setup lang="ts">
import AppSidebar from './AppSidebar.vue'
import LangSwitcher from '@/components/ui/LangSwitcher.vue'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import { Menu, Bell, ChevronDown, LogOut, User } from 'lucide-vue-next'
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const sidebarOpen = ref(false)
const userMenuOpen = ref(false)

const pageTitle = computed(() => {
  const meta = route.meta?.title as string | undefined
  return meta || 'Admin'
})

function getUserInitials(name: string) {
  return (name || 'A').split(' ').slice(0, 2).map((p: string) => p[0]).join('').toUpperCase()
}

async function logout() {
  auth.logout()
  router.push('/login')
}

function onClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (userMenuOpen.value && !target.closest('[data-user-menu]')) {
    userMenuOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', onClickOutside))
onUnmounted(() => document.removeEventListener('click', onClickOutside))
</script>

<template>
  <div class="min-h-screen flex bg-slate-100 dark:bg-slate-950">
    <!-- Mobile sidebar backdrop -->
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-200"
      leave-to-class="opacity-0"
    >
      <div
        v-if="sidebarOpen"
        class="fixed inset-0 z-20 bg-black/50 lg:hidden"
        @click="sidebarOpen = false"
      />
    </Transition>

    <!-- Sidebar -->
    <aside
      class="fixed inset-y-0 left-0 z-30 w-64 transform transition-transform duration-200 lg:static lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <AppSidebar @close="sidebarOpen = false" />
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top bar -->
      <header class="sticky top-0 z-10 flex h-16 items-center gap-4 border-b border-slate-200 bg-white px-6 dark:border-slate-800 dark:bg-slate-900">
        <button
          class="lg:hidden rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
          @click="sidebarOpen = true"
        >
          <Menu :size="20" />
        </button>

        <!-- Page title -->
        <h1 class="text-base font-semibold text-slate-800 dark:text-white hidden sm:block">
          {{ pageTitle }}
        </h1>

        <div class="flex-1" />

        <!-- Theme toggle -->
        <ThemeToggle variant="admin" />

        <!-- Language switcher -->
        <LangSwitcher variant="admin" />

        <!-- Notification bell -->
        <RouterLink
          to="/admin/announcements"
          class="relative rounded-lg p-2 text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800"
        >
          <Bell :size="20" />
        </RouterLink>

        <!-- User menu -->
        <div class="relative" data-user-menu>
          <button
            class="flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
            @click="userMenuOpen = !userMenuOpen"
          >
            <div class="flex h-7 w-7 items-center justify-center rounded-full bg-primary-100 text-xs font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300">
              {{ getUserInitials(auth.user?.full_name || 'Admin') }}
            </div>
            <span class="hidden sm:block max-w-24 truncate">{{ auth.user?.full_name || 'Admin' }}</span>
            <ChevronDown :size="14" class="text-slate-400" />
          </button>

          <div
            v-if="userMenuOpen"
            class="absolute right-0 top-full z-20 mt-1 min-w-44 rounded-xl border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-800"
          >
            <div class="border-b border-slate-100 px-4 py-2 dark:border-slate-700">
              <p class="text-xs font-medium text-slate-800 dark:text-slate-200">{{ auth.user?.full_name }}</p>
              <p class="text-xs text-slate-500">{{ auth.user?.email }}</p>
            </div>
            <RouterLink
              to="/author/profile"
              class="flex items-center gap-2 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 dark:text-slate-300 dark:hover:bg-slate-700"
              @click="userMenuOpen = false"
            >
              <User :size="15" />{{ t('nav.dashboard') }}
            </RouterLink>
            <button
              class="flex w-full items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
              @click="logout"
            >
              <LogOut :size="15" />{{ t('nav.logout') }}
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 p-6 overflow-auto">
        <RouterView />
      </main>
    </div>

  </div>
</template>
