<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import AppNavbar from './AppNavbar.vue'
import AppFooter from './AppFooter.vue'
import JournalLeftSidebar from './JournalLeftSidebar.vue'
import JournalRightSidebar from './JournalRightSidebar.vue'

const route = useRoute()

// Full-width routes (no sidebars) — keep only very wide pages
const fullWidthRoutes: string[] = []
const showSidebars = computed(() => !fullWidthRoutes.includes(route.name as string))
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-900">
    <AppNavbar />
    <main class="flex-1">
      <template v-if="showSidebars">
        <div class="mx-auto max-w-[1400px] px-4 py-6 sm:px-6 lg:px-8">
          <div class="grid gap-6 lg:grid-cols-[240px_1fr_280px]">
            <!-- Left sidebar -->
            <div class="hidden lg:block">
              <JournalLeftSidebar />
            </div>
            <!-- Main content -->
            <div class="min-w-0">
              <RouterView />
            </div>
            <!-- Right sidebar -->
            <div class="hidden lg:block">
              <JournalRightSidebar />
            </div>
          </div>
        </div>
      </template>
      <template v-else>
        <RouterView />
      </template>
    </main>
    <AppFooter />
  </div>
</template>
