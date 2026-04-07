<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { UploadCloud, FileText, X, CheckCircle, AlertCircle } from 'lucide-vue-next'
import axios from 'axios'

interface Props {
  modelValue?: string | null   // s3_key after upload
  fileName?: string | null
  fileSize?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: null,
  fileName: null,
  fileSize: null,
})

const emit = defineEmits<{
  'update:modelValue': [key: string | null]
  'update:fileName': [name: string | null]
  'update:fileSize': [size: number | null]
  uploaded: [{ s3_key: string; filename: string; file_size: number }]
}>()

const { t } = useI18n()

const dragOver = ref(false)
const uploading = ref(false)
const progress = ref(0)
const error = ref('')
const uploadedKey = ref(props.modelValue ?? null)
const uploadedName = ref(props.fileName ?? null)
const uploadedSize = ref(props.fileSize ?? null)

const fileInput = ref<HTMLInputElement | null>(null)

const MAX_SIZE = 20 * 1024 * 1024

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function validate(file: File): string {
  if (file.type !== 'application/pdf') return t('upload.pdfOnly')
  if (file.size > MAX_SIZE) return t('upload.maxSize')
  return ''
}

async function uploadFile(file: File) {
  const err = validate(file)
  if (err) {
    error.value = err
    return
  }

  error.value = ''
  uploading.value = true
  progress.value = 0

  const formData = new FormData()
  formData.append('file', file)

  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.post('/api/upload/pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: token ? `Bearer ${token}` : '',
      },
      onUploadProgress(evt) {
        if (evt.total) {
          progress.value = Math.round((evt.loaded / evt.total) * 100)
        }
      },
    })

    const data = res.data as { s3_key: string; filename: string; file_size: number }
    uploadedKey.value = data.s3_key
    uploadedName.value = data.filename
    uploadedSize.value = data.file_size

    emit('update:modelValue', data.s3_key)
    emit('update:fileName', data.filename)
    emit('update:fileSize', data.file_size)
    emit('uploaded', data)
  } catch (e: any) {
    error.value = e?.response?.data?.detail ?? t('common.error')
    uploadedKey.value = null
  } finally {
    uploading.value = false
  }
}

function onFileSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) uploadFile(file)
  input.value = ''
}

function onDrop(event: DragEvent) {
  dragOver.value = false
  const file = event.dataTransfer?.files[0]
  if (file) uploadFile(file)
}

function removeFile() {
  uploadedKey.value = null
  uploadedName.value = null
  uploadedSize.value = null
  emit('update:modelValue', null)
  emit('update:fileName', null)
  emit('update:fileSize', null)
}
</script>

<template>
  <div>
    <!-- Success state -->
    <div
      v-if="uploadedKey"
      class="flex items-center gap-3 rounded-xl border border-green-200 bg-green-50 p-4 dark:border-green-900/50 dark:bg-green-950/20"
    >
      <CheckCircle :size="22" class="shrink-0 text-green-500" />
      <div class="min-w-0 flex-1">
        <p class="truncate text-sm font-medium text-slate-900 dark:text-white">{{ uploadedName }}</p>
        <p class="text-xs text-slate-400">{{ uploadedSize ? formatSize(uploadedSize) : '' }}</p>
      </div>
      <button
        type="button"
        class="rounded-lg p-1.5 text-slate-400 hover:bg-green-100 hover:text-slate-600 dark:hover:bg-green-900/40"
        @click="removeFile"
      >
        <X :size="16" />
      </button>
    </div>

    <!-- Upload zone -->
    <div v-else>
      <div
        class="relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-10 text-center transition-colors cursor-pointer select-none"
        :class="[
          dragOver
            ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/20'
            : 'border-slate-300 bg-slate-50 hover:border-primary-400 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-primary-600 dark:hover:bg-slate-800',
          uploading ? 'pointer-events-none opacity-60' : '',
        ]"
        @dragover.prevent="dragOver = true"
        @dragleave="dragOver = false"
        @drop.prevent="onDrop"
        @click="fileInput?.click()"
      >
        <UploadCloud
          :size="42"
          :class="dragOver ? 'text-primary-500' : 'text-slate-400 dark:text-slate-600'"
        />
        <p class="mt-3 text-sm font-medium text-slate-700 dark:text-slate-300">
          {{ t('upload.dragDrop') }}
        </p>
        <p class="mt-1 text-xs text-slate-400">{{ t('upload.pdfOnly') }} · {{ t('upload.maxSize') }}</p>

        <input
          ref="fileInput"
          type="file"
          accept="application/pdf"
          class="hidden"
          @change="onFileSelected"
        />
      </div>

      <!-- Upload progress -->
      <div v-if="uploading" class="mt-3">
        <div class="mb-1 flex justify-between text-xs text-slate-500">
          <span>{{ t('upload.uploading') }}</span>
          <span>{{ progress }}%</span>
        </div>
        <div class="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
          <div
            class="h-full rounded-full bg-primary-600 transition-all duration-200"
            :style="{ width: `${progress}%` }"
          />
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" class="mt-2 flex items-center gap-1.5 text-xs text-red-500">
        <AlertCircle :size="13" />
        {{ error }}
      </div>
    </div>
  </div>
</template>
