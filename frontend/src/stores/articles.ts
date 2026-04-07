import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Article, ArticleListItem, PaginatedResponse } from '@/types/article'
import { api } from '@/composables/useApi'

interface ArticleFilters {
  page?: number
  limit?: number
  search?: string
  category?: string
  volume_id?: string
  issue_id?: string
  lang?: string
}

export const useArticlesStore = defineStore('articles', () => {
  const articles = ref<ArticleListItem[]>([])
  const currentArticle = ref<Article | null>(null)
  const total = ref(0)
  const pages = ref(0)
  const currentPage = ref(1)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchArticles(filters: ArticleFilters = {}): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      Object.entries(filters).forEach(([key, val]) => {
        if (val !== undefined && val !== null && val !== '') {
          params.set(key, String(val))
        }
      })
      const data = await api.get<PaginatedResponse<ArticleListItem>>(
        `/api/articles?${params.toString()}`
      )
      articles.value = data.items
      total.value = data.total
      pages.value = data.pages
      currentPage.value = data.page
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load articles'
    } finally {
      loading.value = false
    }
  }

  async function fetchArticle(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentArticle.value = await api.get<Article>(`/api/articles/${id}`)
    } catch (err: unknown) {
      error.value = err instanceof Error ? err.message : 'Failed to load article'
    } finally {
      loading.value = false
    }
  }

  return {
    articles,
    currentArticle,
    total,
    pages,
    currentPage,
    loading,
    error,
    fetchArticles,
    fetchArticle,
  }
})
