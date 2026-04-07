<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { Camera, Loader2, AlertCircle } from 'lucide-vue-next'
import axios from 'axios'

interface Props {
  currentUrl?: string | null
  name?: string
}

const props = withDefaults(defineProps<Props>(), { currentUrl: null, name: '' })
const emit = defineEmits<{ uploaded: [url: string] }>()

const { t } = useI18n()
const uploading = ref(false)
const error = ref('')
const previewUrl = ref<string | null>(props.currentUrl ?? null)
const fileInput = ref<HTMLInputElement | null>(null)

const initials = computed(() => {
  if (!props.name) return '?'
  return props.name
    .trim()
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('')
})

const MAX_SIZE = 5 * 1024 * 1024
const ALLOWED = ['image/jpeg', 'image/png', 'image/webp']

async function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  input.value = ''
  if (!file) return

  if (!ALLOWED.includes(file.type)) {
    error.value = 'Only JPEG, PNG or WebP images are allowed'
    return
  }
  if (file.size > MAX_SIZE) {
    error.value = 'File size exceeds 5MB'
    return
  }

  error.value = ''
  uploading.value = true

  // Show local preview immediately
  const reader = new FileReader()
  reader.onload = (e) => { previewUrl.value = e.target?.result as string }
  reader.readAsDataURL(file)

  const formData = new FormData()
  formData.append('file', file)

  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.post('/api/upload/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: token ? `Bearer ${token}` : '',
      },
    })
    const url: string = res.data.url
    previewUrl.value = url
    emit('uploaded', url)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? t('common.error')
    previewUrl.value = props.currentUrl ?? null
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="flex flex-col items-center gap-3">
    <!-- Avatar circle -->
    <button
      type="button"
      class="group relative h-24 w-24 overflow-hidden rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      :disabled="uploading"
      @click="fileInput?.click()"
    >
      <!-- Image or initials -->
      <img
        v-if="previewUrl"
        :src="previewUrl"
        alt="Avatar"
        class="h-full w-full object-cover"
      />
      <div
        v-else
        class="flex h-full w-full items-center justify-center bg-primary-100 text-2xl font-bold text-primary-700 dark:bg-primary-950 dark:text-primary-300"
      >
        {{ initials }}
      </div>

      <!-- Hover overlay -->
      <div class="absolute inset-0 flex flex-col items-center justify-center bg-black/40 opacity-0 transition-opacity group-hover:opacity-100">
        <Loader2 v-if="uploading" :size="20" class="animate-spin text-white" />
        <Camera v-else :size="20" class="text-white" />
        <span class="mt-1 text-xs text-white">{{ t('author.profile.change_avatar') }}</span>
      </div>
    </button>

    <input
      ref="fileInput"
      type="file"
      accept="image/jpeg,image/png,image/webp"
      class="hidden"
      @change="onFileSelected"
    />

    <p class="text-xs text-slate-400">{{ t('author.profile.avatar_hint') }}</p>

    <p v-if="error" class="flex items-center gap-1 text-xs text-red-500">
      <AlertCircle :size="12" />{{ error }}
    </p>
  </div>
</template>
