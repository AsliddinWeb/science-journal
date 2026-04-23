<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'
import { Mail, Phone, MapPin, Send, CheckCircle, AlertCircle, ExternalLink } from 'lucide-vue-next'
import { api } from '@/composables/useApi'
import { useSeoMeta } from '@/composables/useSeoMeta'

const { t } = useI18n()

useSeoMeta({
  title: t('nav.contact'),
  canonical: `${window.location.origin}/contact`,
  ogUrl: `${window.location.origin}/contact`,
})

const form = reactive({
  name: '',
  email: '',
  subject: '',
  message: '',
})

const errors = reactive({
  name: '',
  email: '',
  subject: '',
  message: '',
})

const submitting = ref(false)
const submitted = ref(false)
const submitError = ref(false)

function validate(): boolean {
  let valid = true
  errors.name = ''
  errors.email = ''
  errors.subject = ''
  errors.message = ''

  if (!form.name.trim()) {
    errors.name = t('contact.error_required')
    valid = false
  }
  if (!form.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = t('contact.error_email')
    valid = false
  }
  if (!form.subject.trim()) {
    errors.subject = t('contact.error_required')
    valid = false
  }
  if (form.message.trim().length < 20) {
    errors.message = t('contact.error_message_min')
    valid = false
  }
  return valid
}

async function onSubmit() {
  if (!validate()) return
  submitting.value = true
  submitError.value = false
  try {
    await api.post('/api/contact', { ...form })
    submitted.value = true
    form.name = ''
    form.email = ''
    form.subject = ''
    form.message = ''
  } catch {
    submitError.value = true
  } finally {
    submitting.value = false
  }
}

const contactInfo = [
  { icon: Mail, label: 'editor@journal.uz', href: 'mailto:editor@journal.uz' },
  { icon: Phone, label: '+998 71 123 45 67', href: 'tel:+998711234567' },
  { icon: MapPin, label: '1 University St, Tashkent, Uzbekistan', href: null },
]
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="rounded-2xl border border-journal-700 bg-gradient-to-r from-journal-800 to-journal-700 p-6 shadow-sm sm:p-8">
      <h1 class="font-serif text-2xl font-bold text-primary-200 sm:text-3xl">{{ t('contact.title') }}</h1>
      <p class="mt-1 text-sm text-slate-300">{{ t('contact.subtitle') }}</p>
    </section>

    <div>
      <div class="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_360px]">

        <!-- ─── Form ─── -->
        <div>
          <!-- Success state -->
          <div
            v-if="submitted"
            class="flex flex-col items-center justify-center rounded-2xl border border-green-200 bg-green-50 py-16 text-center dark:border-green-900/50 dark:bg-green-950/20"
          >
            <CheckCircle :size="56" class="text-green-500" />
            <h2 class="mt-4 font-serif text-2xl font-bold text-journal-800 dark:text-primary-300">
              {{ t('contact.success_title') }}
            </h2>
            <p class="mt-2 text-slate-500 dark:text-slate-400">{{ t('contact.success_desc') }}</p>
            <button class="btn-primary mt-6" @click="submitted = false">
              {{ t('contact.send_another') }}
            </button>
          </div>

          <!-- Form -->
          <form v-else @submit.prevent="onSubmit" class="space-y-5">
            <!-- Error banner -->
            <div v-if="submitError" class="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900/50 dark:bg-red-950/20 dark:text-red-400">
              <AlertCircle :size="18" />
              {{ t('common.error') }}
            </div>

            <!-- Name -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('contact.name') }} *
              </label>
              <input
                v-model="form.name"
                type="text"
                :placeholder="t('contact.name_placeholder')"
                class="input-base"
                :class="{ 'border-red-400 focus:border-red-400 focus:ring-red-400': errors.name }"
              />
              <p v-if="errors.name" class="mt-1 text-xs text-red-500">{{ errors.name }}</p>
            </div>

            <!-- Email -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('contact.email') }} *
              </label>
              <input
                v-model="form.email"
                type="email"
                :placeholder="t('contact.email_placeholder')"
                class="input-base"
                :class="{ 'border-red-400 focus:border-red-400 focus:ring-red-400': errors.email }"
              />
              <p v-if="errors.email" class="mt-1 text-xs text-red-500">{{ errors.email }}</p>
            </div>

            <!-- Subject -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('contact.subject') }} *
              </label>
              <input
                v-model="form.subject"
                type="text"
                :placeholder="t('contact.subject_placeholder')"
                class="input-base"
                :class="{ 'border-red-400 focus:border-red-400 focus:ring-red-400': errors.subject }"
              />
              <p v-if="errors.subject" class="mt-1 text-xs text-red-500">{{ errors.subject }}</p>
            </div>

            <!-- Message -->
            <div>
              <label class="mb-1.5 block text-sm font-medium text-slate-700 dark:text-slate-300">
                {{ t('contact.message') }} *
              </label>
              <textarea
                v-model="form.message"
                rows="6"
                :placeholder="t('contact.message_placeholder')"
                class="input-base resize-none"
                :class="{ 'border-red-400 focus:border-red-400 focus:ring-red-400': errors.message }"
              />
              <div class="mt-1 flex items-center justify-between">
                <p v-if="errors.message" class="text-xs text-red-500">{{ errors.message }}</p>
                <span class="ml-auto text-xs text-slate-400">{{ form.message.length }} / 2000</span>
              </div>
            </div>

            <!-- Submit -->
            <button
              type="submit"
              class="btn-primary w-full py-3"
              :disabled="submitting"
            >
              <Send :size="16" :class="{ 'animate-pulse': submitting }" />
              {{ submitting ? t('contact.sending') : t('contact.send') }}
            </button>
          </form>
        </div>

        <!-- ─── Right: contact info ─── -->
        <div class="space-y-6">
          <!-- Contact details -->
          <div class="card p-6 space-y-4">
            <h2 class="font-serif text-lg font-bold text-journal-800 dark:text-primary-300">
              {{ t('contact.get_in_touch') }}
            </h2>
            <div v-for="info in contactInfo" :key="info.label" class="flex items-start gap-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary-50 dark:bg-primary-950">
                <component :is="info.icon" :size="17" class="text-primary-600 dark:text-primary-400" />
              </div>
              <div class="pt-1">
                <a
                  v-if="info.href"
                  :href="info.href"
                  class="text-sm text-slate-700 transition-colors hover:text-primary-600 dark:text-slate-300 dark:hover:text-primary-400"
                >
                  {{ info.label }}
                </a>
                <span v-else class="text-sm text-slate-700 dark:text-slate-300">{{ info.label }}</span>
              </div>
            </div>

            <!-- Telegram -->
            <a
              href="https://t.me/scienceinnovationjournal"
              target="_blank"
              rel="noopener noreferrer"
              class="mt-2 flex items-center gap-2 rounded-xl border border-blue-200 bg-blue-50 px-4 py-3 text-sm font-medium text-blue-700 transition-colors hover:bg-blue-100 dark:border-blue-900 dark:bg-blue-950/30 dark:text-blue-400 dark:hover:bg-blue-950/50"
            >
              <ExternalLink :size="15" />
              Telegram Channel
            </a>
          </div>

          <!-- Map placeholder -->
          <div class="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-800">
            <div class="flex h-48 items-center justify-center bg-slate-100 dark:bg-slate-900">
              <div class="text-center">
                <MapPin :size="32" class="mx-auto text-slate-300 dark:text-slate-700" />
                <p class="mt-2 text-sm text-slate-400 dark:text-slate-600">Tashkent, Uzbekistan</p>
              </div>
            </div>
          </div>

          <!-- Working hours -->
          <div class="card p-5">
            <h3 class="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">
              {{ t('contact.working_hours') }}
            </h3>
            <div class="space-y-1.5 text-sm text-slate-500 dark:text-slate-400">
              <div class="flex justify-between">
                <span>{{ t('contact.weekdays') }}</span>
                <span class="font-medium text-slate-700 dark:text-slate-300">09:00 – 18:00</span>
              </div>
              <div class="flex justify-between">
                <span>{{ t('contact.saturday') }}</span>
                <span class="font-medium text-slate-700 dark:text-slate-300">10:00 – 15:00</span>
              </div>
              <div class="flex justify-between">
                <span>{{ t('contact.sunday') }}</span>
                <span class="font-medium text-slate-700 dark:text-slate-300">{{ t('contact.closed') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
