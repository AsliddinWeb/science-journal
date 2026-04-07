<script setup lang="ts">
interface Props {
  size?: number
  class?: string
}
const props = withDefaults(defineProps<Props>(), { size: 20 })
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    class="animate-spin"
    :class="$props.class"
  >
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      stroke-width="3"
      stroke-dasharray="60"
      stroke-dashoffset="20"
      stroke-linecap="round"
      opacity="0.3"
    />
    <path
      d="M12 2a10 10 0 0 1 10 10"
      stroke="currentColor"
      stroke-width="3"
      stroke-linecap="round"
    />
  </svg>
</template>
