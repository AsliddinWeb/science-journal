<script setup lang="ts">
import { computed } from 'vue'
import { BookOpen } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  src?: string | null
  alt?: string
  height?: string
  rounded?: string
}>(), {
  alt: '',
  height: 'h-48',
  rounded: 'rounded-xl',
})

const resolvedSrc = computed(() => {
  if (!props.src) return null
  return props.src.startsWith('/') ? props.src : `/api/uploads/${props.src}`
})

// Deterministic gradient from text
const gradient = computed(() => {
  const text = props.alt || 'A'
  let hash = 0
  for (let i = 0; i < text.length; i++) hash = text.charCodeAt(i) + ((hash << 5) - hash)

  const gradients = [
    'from-blue-600 to-indigo-700',
    'from-emerald-600 to-teal-700',
    'from-violet-600 to-purple-700',
    'from-rose-600 to-pink-700',
    'from-amber-600 to-orange-700',
    'from-cyan-600 to-blue-700',
    'from-fuchsia-600 to-pink-700',
    'from-lime-600 to-green-700',
  ]
  return gradients[Math.abs(hash) % gradients.length]
})

const initials = computed(() => {
  const words = (props.alt || 'J').split(/\s+/).filter(Boolean)
  if (words.length >= 2) return (words[0][0] + words[1][0]).toUpperCase()
  return words[0]?.substring(0, 2).toUpperCase() || 'J'
})
</script>

<template>
  <div :class="[height, rounded, 'overflow-hidden relative']">
    <!-- Real image -->
    <img
      v-if="resolvedSrc"
      :src="resolvedSrc"
      :alt="alt"
      class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
      loading="lazy"
      @error="($event.target as HTMLImageElement).style.display = 'none'; ($event.target as HTMLImageElement).nextElementSibling?.classList.remove('hidden')"
    />
    <!-- Placeholder (shown if no src or image fails to load) -->
    <div
      :class="[
        'flex flex-col items-center justify-center bg-gradient-to-br text-white',
        gradient,
        resolvedSrc ? 'hidden' : '',
        'absolute inset-0',
      ]"
    >
      <BookOpen :size="32" class="mb-2 opacity-40" />
      <span class="text-2xl font-bold opacity-70">{{ initials }}</span>
    </div>
  </div>
</template>
