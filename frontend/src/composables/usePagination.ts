import { ref, computed } from 'vue'

export function usePagination(initialLimit = 10) {
  const page = ref(1)
  const limit = ref(initialLimit)
  const total = ref(0)
  const pages = ref(0)

  const hasPrev = computed(() => page.value > 1)
  const hasNext = computed(() => page.value < pages.value)

  function setPage(p: number) {
    page.value = p
  }

  function nextPage() {
    if (hasNext.value) page.value++
  }

  function prevPage() {
    if (hasPrev.value) page.value--
  }

  function setTotal(t: number) {
    total.value = t
    pages.value = Math.ceil(t / limit.value)
  }

  return {
    page,
    limit,
    total,
    pages,
    hasPrev,
    hasNext,
    setPage,
    nextPage,
    prevPage,
    setTotal,
  }
}
