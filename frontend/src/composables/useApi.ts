import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { useCache } from '@/composables/useCache'

let axiosInstance: AxiosInstance | null = null

const cache = useCache()

// Endpoints that get cached and their TTL in seconds
const CACHE_RULES: { pattern: RegExp; ttl: number; prefix: string }[] = [
  { pattern: /^\/api\/articles(\?|$)/, ttl: 60, prefix: 'articles:' },
  { pattern: /^\/api\/volumes(\?|$)/, ttl: 300, prefix: 'volumes:' },
  { pattern: /^\/api\/editorial(\?|$)/, ttl: 600, prefix: 'editorial:' },
  { pattern: /^\/api\/stats\/overview/, ttl: 300, prefix: 'stats:' },
  { pattern: /^\/api\/indexing/, ttl: 600, prefix: 'indexing:' },
  { pattern: /^\/api\/categories/, ttl: 600, prefix: 'categories:' },
]

function getCacheRule(url: string) {
  return CACHE_RULES.find((r) => r.pattern.test(url)) ?? null
}

function prefixesAffectedByMutation(url: string): string[] {
  const affected: string[] = []
  if (url.includes('/api/articles')) affected.push('articles:')
  if (url.includes('/api/volumes')) affected.push('volumes:')
  if (url.includes('/api/editorial')) affected.push('editorial:')
  if (url.includes('/api/stats')) affected.push('stats:')
  return affected
}

function getAxios(): AxiosInstance {
  if (axiosInstance) return axiosInstance

  axiosInstance = axios.create({
    baseURL: import.meta.env.VITE_API_URL || '',
    timeout: 30000,
    headers: { 'Content-Type': 'application/json' },
  })

  axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  })

  axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const original = error.config
      if (error.response?.status === 401 && !original._retry) {
        original._retry = true
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          try {
            const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('refresh_token', data.refresh_token)
            original.headers.Authorization = `Bearer ${data.access_token}`
            return axiosInstance!(original)
          } catch {
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
          }
        }
      }
      return Promise.reject(error)
    }
  )

  return axiosInstance
}

export const api = {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const rule = getCacheRule(url)
    if (rule) {
      const cacheKey = `${rule.prefix}${url}`
      const cached = cache.get<T>(cacheKey)
      if (cached !== null) return cached
      const { data } = await getAxios().get<T>(url, config)
      cache.set(cacheKey, data, rule.ttl)
      return data
    }
    const { data } = await getAxios().get<T>(url, config)
    return data
  },

  async post<T>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> {
    prefixesAffectedByMutation(url).forEach((p) => cache.invalidatePrefix(p))
    const { data } = await getAxios().post<T>(url, body, config)
    return data
  },

  async put<T>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> {
    prefixesAffectedByMutation(url).forEach((p) => cache.invalidatePrefix(p))
    const { data } = await getAxios().put<T>(url, body, config)
    return data
  },

  async patch<T>(url: string, body?: unknown, config?: AxiosRequestConfig): Promise<T> {
    prefixesAffectedByMutation(url).forEach((p) => cache.invalidatePrefix(p))
    const { data } = await getAxios().patch<T>(url, body, config)
    return data
  },

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    prefixesAffectedByMutation(url).forEach((p) => cache.invalidatePrefix(p))
    const { data } = await getAxios().delete<T>(url, config)
    return data
  },
}

export function useApi() {
  return api
}
