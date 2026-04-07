<script setup lang="ts">
import { ref } from 'vue'
import { Search, X } from 'lucide-vue-next'

interface Props {
  modelValue: string
  placeholder?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: 'Search...',
  loading: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  search: [value: string]
}>()

const inputRef = ref<HTMLInputElement>()

function handleInput(e: Event) {
  emit('update:modelValue', (e.target as HTMLInputElement).value)
}

function handleSubmit() {
  emit('search', props.modelValue)
}

function clear() {
  emit('update:modelValue', '')
  emit('search', '')
  inputRef.value?.focus()
}
</script>

<template>
  <form class="relative" @submit.prevent="handleSubmit">
    <div class="pointer-events-none absolute inset-y-0 left-3.5 flex items-center">
      <Search :size="18" class="text-slate-400" />
    </div>
    <input
      ref="inputRef"
      :value="modelValue"
      :placeholder="placeholder"
      type="search"
      class="input-base pl-10 pr-10"
      @input="handleInput"
      @keydown.enter.prevent="handleSubmit"
    />
    <button
      v-if="modelValue"
      type="button"
      class="absolute inset-y-0 right-3 flex items-center text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
      @click="clear"
    >
      <X :size="16" />
    </button>
  </form>
</template>
