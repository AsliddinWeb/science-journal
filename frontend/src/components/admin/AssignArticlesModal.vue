<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { X } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useLocaleStore } from '@/stores/locale'
import { getLocalizedField } from '@/utils/truncate'
import { useToast } from '@/composables/useToast'
import AppButton from '@/components/ui/AppButton.vue'
import AppSpinner from '@/components/ui/AppSpinner.vue'
import type { Article } from '@/types/article'

const props = defineProps<{
  issueId: string
}>()

const emit = defineEmits<{
  close: []
  assigned: []
}>()

const localeStore = useLocaleStore()
const toast = useToast()
const articles = ref<Article[]>([])
const selected = ref<Set<string>>(new Set())
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  try {
    const data = await api.get<any>('/api/admin/articles?status=accepted&limit=100')
    articles.value = (data.items || []).filter((a: Article) => !a.issue_id)
  } finally {
    loading.value = false }
})

function toggle(id: string) {
  if (selected.value.has(id)) selected.value.delete(id)
  else selected.value.add(id)
}

const selectedCount = computed(() => selected.value.size)

async function assign() {
  if (!selected.value.size) return
  saving.value = true
  try {
    await api.patch('/api/admin/articles/bulk-assign', {
      article_ids: Array.from(selected.value),
      issue_id: props.issueId,
    })
    toast.success('Maqolalar tayinlandi')
    emit('assigned')
    emit('close')
  } catch {
    toast.error('Tayinlashda xatolik')
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" @click="emit('close')" />
      <div class="relative flex w-full max-w-2xl flex-col rounded-2xl bg-white shadow-xl dark:bg-slate-800" style="max-height: 80vh">
        <div class="flex items-center justify-between border-b border-slate-200 px-6 py-4 dark:border-slate-700">
          <h3 class="font-semibold text-slate-900 dark:text-white">Qabul qilingan maqolalarni tayinlash</h3>
          <button class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700" @click="emit('close')">
            <X :size="18" />
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6">
          <div v-if="loading" class="flex justify-center py-8">
            <AppSpinner :size="28" class="text-primary-500" />
          </div>
          <div v-else-if="!articles.length" class="py-8 text-center text-slate-500">
            Tayinlanmagan qabul qilingan maqolalar yo'q
          </div>
          <div v-else class="flex flex-col gap-2">
            <label
              v-for="article in articles"
              :key="article.id"
              class="flex cursor-pointer items-start gap-3 rounded-lg border p-3 transition hover:bg-slate-50 dark:hover:bg-slate-700"
              :class="selected.has(article.id) ? 'border-primary-400 bg-primary-50 dark:bg-primary-950/30' : 'border-slate-200 dark:border-slate-700'"
            >
              <input
                type="checkbox"
                :checked="selected.has(article.id)"
                class="mt-0.5 h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                @change="toggle(article.id)"
              />
              <div class="flex-1 min-w-0">
                <p class="line-clamp-1 text-sm font-medium text-slate-900 dark:text-white">
                  {{ getLocalizedField(article.title, localeStore.current) || 'Sarlavhasiz' }}
                </p>
                <p class="text-xs text-slate-500">{{ article.author?.full_name }}</p>
              </div>
            </label>
          </div>
        </div>

        <div class="flex items-center justify-between border-t border-slate-200 px-6 py-4 dark:border-slate-700">
          <span class="text-sm text-slate-500">{{ selectedCount }} ta tanlandi</span>
          <div class="flex gap-3">
            <AppButton variant="ghost" @click="emit('close')">Bekor qilish</AppButton>
            <AppButton :loading="saving" :disabled="!selectedCount" @click="assign">
              Tayinlash
            </AppButton>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>
