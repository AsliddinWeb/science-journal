<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Menu, X, Search, ChevronDown, BookOpen, FileText, Users, Shield, Info, BookMarked, Globe2, PenLine, LogIn } from 'lucide-vue-next'
import { useI18n } from 'vue-i18n'
import ThemeToggle from '@/components/ui/ThemeToggle.vue'
import LangSwitcher from '@/components/ui/LangSwitcher.vue'
import { useAuthStore } from '@/stores/auth'
import { useSiteInfoStore } from '@/stores/siteInfo'

const { t } = useI18n()
const siteInfo = useSiteInfoStore()
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const mobileMenuOpen = ref(false)
const userMenuOpen = ref(false)
const forAuthorsOpen = ref(false)
const aboutOpen = ref(false)

// Close dropdowns on route change
router.afterEach(() => {
  mobileMenuOpen.value = false
  userMenuOpen.value = false
  forAuthorsOpen.value = false
  aboutOpen.value = false
})

function handleClickOutside(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('[data-dropdown]')) {
    userMenuOpen.value = false
    forAuthorsOpen.value = false
    aboutOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))

function toggleForAuthors() {
  forAuthorsOpen.value = !forAuthorsOpen.value
  aboutOpen.value = false
  userMenuOpen.value = false
}
function toggleAbout() {
  aboutOpen.value = !aboutOpen.value
  forAuthorsOpen.value = false
  userMenuOpen.value = false
}
function toggleUser() {
  userMenuOpen.value = !userMenuOpen.value
  forAuthorsOpen.value = false
  aboutOpen.value = false
}

async function handleLogout() {
  await authStore.logout()
  userMenuOpen.value = false
  router.push({ name: 'home' })
}

function getInitials(name: string): string {
  return name.split(' ').map((n) => n[0]).slice(0, 2).join('').toUpperCase()
}

const forAuthorsLinks = computed(() => [
  { to: '/pages/author-guidelines', icon: FileText, label: t('nav.author_guidelines') },
  { to: '/pages/review-process', icon: Shield, label: t('nav.review_process') },
  { to: '/pages/open-access', icon: Globe2, label: t('nav.open_access') },
])

const aboutLinks = computed(() => [
  { to: '/pages/about', icon: Info, label: t('nav.about_journal') },
  { to: '/pages/aims', icon: BookMarked, label: t('nav.aims_scope') },
  { to: '/editorial-board', icon: Users, label: t('nav.editorial') },
  { to: '/contact', icon: Globe2, label: t('nav.contact') },
  { to: '/pages/indexing', icon: Globe2, label: t('nav.indexing') },
])

const isActive = (path: string) => route.path.startsWith(path)
</script>

<template>
  <header class="sticky top-0 z-50 bg-gradient-to-b from-journal-800 via-journal-700 to-journal-800 shadow-lg">
    <nav class="mx-auto max-w-[1400px] px-4 sm:px-6 lg:px-8">
      <div class="flex h-20 items-center justify-between gap-4">

        <!-- Logo + journal name (configurable via admin home-settings) -->
        <RouterLink to="/" class="flex items-center gap-3 shrink-0">
          <div class="flex shrink-0 items-center justify-center">
            <template v-if="!siteInfo.loaded">
              <div class="skeleton h-11 w-11 rounded-lg" />
            </template>
            <template v-else>
              <img
                v-if="siteInfo.logoUrl"
                :src="siteInfo.logoUrl"
                :alt="siteInfo.siteName"
                class="h-12 w-auto max-w-[140px] object-contain"
              />
              <div v-else class="flex h-11 w-11 items-center justify-center rounded-lg bg-primary-500 shadow-md">
                <BookOpen :size="22" class="text-white" />
              </div>
            </template>
          </div>
          <div class="hidden sm:flex sm:flex-col sm:leading-tight">
            <template v-if="!siteInfo.loaded">
              <div class="skeleton h-3 w-20 rounded" />
              <div class="skeleton mt-1.5 h-4 w-40 rounded" />
            </template>
            <template v-else>
              <span v-if="siteInfo.tagline" class="text-[10px] font-semibold uppercase tracking-widest text-primary-300/80">
                {{ siteInfo.tagline }}
              </span>
              <span class="font-serif text-base font-bold text-primary-100 sm:text-lg">
                {{ siteInfo.siteName }}
              </span>
            </template>
          </div>
        </RouterLink>

        <!-- Desktop Nav - hidden since left sidebar has all nav -->
        <ul class="hidden items-center gap-0.5">
          <li>
            <RouterLink
              to="/articles"
              class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
              active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
            >{{ t('nav.articles') }}</RouterLink>
          </li>
          <li>
            <RouterLink
              to="/archive"
              class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
              active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
            >{{ t('nav.archive') }}</RouterLink>
          </li>
          <li>
            <RouterLink
              to="/conferences"
              class="rounded-md px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white"
              active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
            >{{ t('nav.conferences') }}</RouterLink>
          </li>

          <!-- For Authors dropdown -->
          <li class="relative" data-dropdown>
            <button
              class="flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium transition-colors"
              :class="forAuthorsOpen || isActive('/author') || isActive('/pages/author')
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white'"
              @click.stop="toggleForAuthors"
            >
              {{ t('nav.for_authors') }}
              <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': forAuthorsOpen }" />
            </button>
            <Transition
              enter-active-class="transition-all duration-150 ease-out"
              enter-from-class="opacity-0 -translate-y-1 scale-95"
              leave-active-class="transition-all duration-100 ease-in"
              leave-to-class="opacity-0 -translate-y-1 scale-95"
            >
              <div
                v-if="forAuthorsOpen"
                class="absolute left-0 top-full mt-1 w-56 rounded-xl border border-slate-200 bg-white p-1.5 shadow-lg dark:border-slate-700 dark:bg-slate-800"
              >
                <RouterLink
                  v-for="link in forAuthorsLinks"
                  :key="link.to"
                  :to="link.to"
                  class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <component :is="link.icon" :size="15" class="shrink-0 text-primary-600 dark:text-primary-400" />
                  {{ link.label }}
                </RouterLink>
              </div>
            </Transition>
          </li>

          <!-- About dropdown -->
          <li class="relative" data-dropdown>
            <button
              class="flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium transition-colors"
              :class="aboutOpen || isActive('/pages/about') || isActive('/editorial') || isActive('/contact')
                ? 'bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300'
                : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-white'"
              @click.stop="toggleAbout"
            >
              {{ t('nav.about') }}
              <ChevronDown :size="14" class="transition-transform" :class="{ 'rotate-180': aboutOpen }" />
            </button>
            <Transition
              enter-active-class="transition-all duration-150 ease-out"
              enter-from-class="opacity-0 -translate-y-1 scale-95"
              leave-active-class="transition-all duration-100 ease-in"
              leave-to-class="opacity-0 -translate-y-1 scale-95"
            >
              <div
                v-if="aboutOpen"
                class="absolute left-0 top-full mt-1 w-52 rounded-xl border border-slate-200 bg-white p-1.5 shadow-lg dark:border-slate-700 dark:bg-slate-800"
              >
                <RouterLink
                  v-for="link in aboutLinks"
                  :key="link.to"
                  :to="link.to"
                  class="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                >
                  <component :is="link.icon" :size="15" class="shrink-0 text-primary-600 dark:text-primary-400" />
                  {{ link.label }}
                </RouterLink>
              </div>
            </Transition>
          </li>

        </ul>

        <!-- Right side -->
        <div class="flex items-center gap-1.5">
          <RouterLink
            to="/search"
            class="rounded-lg p-2 text-primary-300/80 transition-colors hover:bg-white/10 hover:text-primary-200"
            :title="t('common.search')"
          >
            <Search :size="20" />
          </RouterLink>

          <ThemeToggle />
          <LangSwitcher />

          <!-- Authenticated -->
          <template v-if="authStore.isAuthenticated">
            <div class="relative" data-dropdown>
              <button
                class="flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-sm text-primary-200 transition-colors hover:bg-white/10"
                @click.stop="toggleUser"
              >
                <div
                  v-if="!authStore.user?.avatar_url"
                  class="flex h-7 w-7 items-center justify-center rounded-full bg-primary-600 text-xs font-semibold text-white"
                >
                  {{ authStore.user?.full_name ? getInitials(authStore.user.full_name) : 'U' }}
                </div>
                <img
                  v-else
                  :src="authStore.user.avatar_url"
                  :alt="authStore.user.full_name"
                  class="h-7 w-7 rounded-full object-cover"
                />
                <ChevronDown :size="14" class="hidden sm:block transition-transform" :class="{ 'rotate-180': userMenuOpen }" />
              </button>

              <Transition
                enter-active-class="transition-all duration-150 ease-out"
                enter-from-class="opacity-0 scale-95 -translate-y-1"
                leave-active-class="transition-all duration-100 ease-in"
                leave-to-class="opacity-0 scale-95 -translate-y-1"
              >
                <div
                  v-if="userMenuOpen"
                  class="absolute right-0 top-full z-50 mt-1 w-52 rounded-xl border border-slate-200 bg-white p-1.5 shadow-lg dark:border-slate-700 dark:bg-slate-800"
                >
                  <div class="border-b border-slate-100 px-3 py-2 dark:border-slate-700">
                    <p class="text-sm font-medium text-slate-900 dark:text-white truncate">
                      {{ authStore.user?.full_name }}
                    </p>
                    <p class="text-xs text-slate-500 dark:text-slate-400 truncate">{{ authStore.user?.email }}</p>
                  </div>
                  <div class="mt-1 flex flex-col gap-0.5">
                    <RouterLink
                      to="/author/dashboard"
                      class="flex items-center rounded-lg px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                      @click="userMenuOpen = false"
                    >
                      {{ t('nav.dashboard') }}
                    </RouterLink>
                    <RouterLink
                      v-if="authStore.isAdmin"
                      to="/admin/dashboard"
                      class="flex items-center rounded-lg px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-700"
                      @click="userMenuOpen = false"
                    >
                      Admin Panel
                    </RouterLink>
                    <button
                      class="flex w-full items-center rounded-lg px-3 py-2 text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/50"
                      @click="handleLogout"
                    >
                      {{ t('nav.logout') }}
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </template>

          <!-- Guest -->
          <template v-else>
            <RouterLink
              to="/register"
              class="hidden items-center gap-1.5 rounded-lg border border-primary-400/40 bg-white/5 px-4 py-2 text-sm font-medium text-primary-200 transition hover:bg-white/10 sm:inline-flex"
            >
              {{ t('nav.register') }}
            </RouterLink>
            <RouterLink
              to="/login"
              class="hidden items-center gap-1.5 rounded-lg bg-primary-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-primary-700 sm:inline-flex"
            >
              <LogIn :size="15" />
              {{ t('nav.login') }}
            </RouterLink>
          </template>

          <!-- Mobile hamburger -->
          <button
            class="rounded-lg p-2 text-slate-500 transition-colors hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800 lg:hidden"
            @click="mobileMenuOpen = !mobileMenuOpen"
          >
            <X v-if="mobileMenuOpen" :size="20" />
            <Menu v-else :size="20" />
          </button>
        </div>
      </div>

      <!-- Mobile Drawer -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-2"
        leave-active-class="transition-all duration-150 ease-in"
        leave-to-class="opacity-0 -translate-y-2"
      >
        <div
          v-if="mobileMenuOpen"
          class="border-t border-slate-200 py-4 dark:border-slate-800 lg:hidden"
        >
          <ul class="flex flex-col gap-0.5">
            <li>
              <RouterLink to="/" class="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" exact active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ t('nav.home') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/articles" class="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ t('nav.articles') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/archive" class="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ t('nav.archive') }}
              </RouterLink>
            </li>
            <li>
              <RouterLink to="/conferences" class="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ t('nav.conferences') }}
              </RouterLink>
            </li>
            <!-- For Authors mobile section -->
            <li class="border-t border-slate-100 mt-1 pt-1 dark:border-slate-800">
              <p class="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                {{ t('nav.for_authors') }}
              </p>
              <RouterLink
                v-for="link in forAuthorsLinks"
                :key="link.to"
                :to="link.to"
                class="flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                active-class="text-primary-700 dark:text-primary-300"
              >
                <component :is="link.icon" :size="15" class="text-primary-600 dark:text-primary-400" />
                {{ link.label }}
              </RouterLink>
            </li>
            <!-- About mobile section -->
            <li class="border-t border-slate-100 mt-1 pt-1 dark:border-slate-800">
              <p class="px-3 py-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                {{ t('nav.about') }}
              </p>
              <RouterLink
                v-for="link in aboutLinks"
                :key="link.to"
                :to="link.to"
                class="flex items-center gap-2 rounded-lg px-3 py-2.5 text-sm text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                active-class="text-primary-700 dark:text-primary-300"
              >
                <component :is="link.icon" :size="15" class="text-primary-600 dark:text-primary-400" />
                {{ link.label }}
              </RouterLink>
            </li>
            <li class="border-t border-slate-100 mt-1 pt-1 dark:border-slate-800">
              <RouterLink to="/contact" class="block rounded-lg px-3 py-2.5 text-sm font-medium text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800" active-class="bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300">
                {{ t('nav.contact') }}
              </RouterLink>
            </li>
          </ul>

          <!-- Mobile auth buttons -->
          <div class="mt-4 flex flex-col gap-2 border-t border-slate-100 pt-4 dark:border-slate-800">
            <template v-if="authStore.isAuthenticated">
              <div class="flex items-center gap-3 px-3 py-2">
                <div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-xs font-semibold text-primary-700 dark:bg-primary-900 dark:text-primary-300">
                  {{ authStore.user?.full_name ? getInitials(authStore.user.full_name) : 'U' }}
                </div>
                <div class="min-w-0">
                  <p class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ authStore.user?.full_name }}</p>
                  <p class="text-xs text-slate-500 dark:text-slate-400 truncate">{{ authStore.user?.email }}</p>
                </div>
              </div>
              <RouterLink to="/author/dashboard" class="btn-ghost text-center">{{ t('nav.dashboard') }}</RouterLink>
              <button class="btn-ghost text-center text-red-600 dark:text-red-400" @click="handleLogout">{{ t('nav.logout') }}</button>
            </template>
            <template v-else>
              <RouterLink to="/login" class="btn-ghost text-center">{{ t('nav.login') }}</RouterLink>
              <RouterLink to="/register" class="btn-primary text-center">{{ t('nav.register') }}</RouterLink>
            </template>
          </div>
        </div>
      </Transition>
    </nav>
  </header>
</template>
