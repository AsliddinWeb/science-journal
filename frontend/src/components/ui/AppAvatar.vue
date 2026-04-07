<script setup lang="ts">
import { computed, ref } from 'vue'

type AvatarSize = 'sm' | 'md' | 'lg' | 'xl' | '2xl'

const props = withDefaults(defineProps<{
  name: string
  src?: string | null
  size?: AvatarSize
}>(), {
  src: null,
  size: 'md',
})

const PALETTE = [
  'bg-red-500', 'bg-orange-500', 'bg-amber-500', 'bg-yellow-500',
  'bg-lime-500', 'bg-green-500', 'bg-emerald-500', 'bg-teal-500',
  'bg-cyan-500', 'bg-sky-500', 'bg-blue-500', 'bg-indigo-500',
  'bg-violet-500', 'bg-purple-500', 'bg-fuchsia-500', 'bg-pink-500',
]

const SIZE_MAP: Record<AvatarSize, string> = {
  sm: 'h-6 w-6 text-[10px]',
  md: 'h-8 w-8 text-xs',
  lg: 'h-10 w-10 text-sm',
  xl: 'h-16 w-16 text-lg',
  '2xl': 'h-24 w-24 text-2xl',
}

function hashName(name: string): number {
  let h = 0
  for (let i = 0; i < name.length; i++) h = (h * 31 + name.charCodeAt(i)) >>> 0
  return h
}

const initials = computed(() => {
  const parts = props.name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return props.name.slice(0, 2).toUpperCase()
})

const bgColor = computed(() => PALETTE[hashName(props.name) % PALETTE.length])
const sizeClass = computed(() => SIZE_MAP[props.size])

const imgLoaded = ref(false)
const imgError = ref(false)

function onLoad() { imgLoaded.value = true }
function onError() { imgError.value = true }
</script>

<template>
  <div
    class="relative shrink-0 overflow-hidden rounded-full"
    :class="sizeClass"
  >
    <!-- Fallback initials -->
    <div
      v-if="!src || imgError"
      class="flex h-full w-full items-center justify-center font-semibold text-white"
      :class="bgColor"
    >
      {{ initials }}
    </div>

    <!-- Image -->
    <img
      v-if="src && !imgError"
      :src="src"
      :alt="name"
      loading="lazy"
      class="h-full w-full object-cover transition-opacity duration-200"
      :class="imgLoaded ? 'opacity-100' : 'opacity-0'"
      @load="onLoad"
      @error="onError"
    />

    <!-- Skeleton while loading -->
    <div
      v-if="src && !imgLoaded && !imgError"
      class="absolute inset-0 animate-pulse rounded-full bg-slate-200 dark:bg-slate-700"
    />
  </div>
</template>
