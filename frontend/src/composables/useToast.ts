import { ref } from 'vue'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

export interface Toast {
  id: number
  message: string
  type: ToastType
  duration: number
}

const toasts = ref<Toast[]>([])
let nextId = 0

export function useToast() {
  function show(message: string, type: ToastType = 'info', duration = 4000) {
    const id = ++nextId
    toasts.value.push({ id, message, type, duration })
    setTimeout(() => {
      dismiss(id)
    }, duration)
  }

  function dismiss(id: number) {
    const idx = toasts.value.findIndex((t) => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  const success = (msg: string, duration?: number) => show(msg, 'success', duration)
  const error = (msg: string, duration?: number) => show(msg, 'error', duration)
  const warning = (msg: string, duration?: number) => show(msg, 'warning', duration)
  const info = (msg: string, duration?: number) => show(msg, 'info', duration)

  return { toasts, show, dismiss, success, error, warning, info }
}
