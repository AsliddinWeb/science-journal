<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  src: string
  alt: string
  fallback?: string
  class?: string
  width?: number | string
  height?: number | string
}>()

const loaded = ref(false)
const errored = ref(false)

function onLoad() {
  loaded.value = true
}

function onError() {
  errored.value = true
  loaded.value = true
}

const fallbackSrc = props.fallback || `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E`
</script>

<template>
  <div class="relative overflow-hidden" :class="props.class">
    <!-- Skeleton placeholder while loading -->
    <div
      v-if="!loaded"
      class="absolute inset-0 animate-pulse bg-slate-200 dark:bg-slate-700"
    />
    <img
      :src="errored ? fallbackSrc : src"
      :alt="alt"
      :width="width"
      :height="height"
      loading="lazy"
      decoding="async"
      class="w-full h-full object-cover transition-opacity duration-300"
      :class="loaded ? 'opacity-100' : 'opacity-0'"
      @load="onLoad"
      @error="onError"
    />
  </div>
</template>
