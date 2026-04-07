import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginCredentials, RegisterData, TokenResponse } from '@/types/user'
import { api } from '@/composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() =>
    user.value?.role === 'superadmin' || user.value?.role === 'editor'
  )
  const isReviewer = computed(() =>
    ['superadmin', 'editor', 'reviewer'].includes(user.value?.role ?? '')
  )

  function setTokens(tokens: TokenResponse) {
    accessToken.value = tokens.access_token
    refreshToken.value = tokens.refresh_token
    localStorage.setItem('access_token', tokens.access_token)
    localStorage.setItem('refresh_token', tokens.refresh_token)
  }

  function clearAuth() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  async function login(credentials: LoginCredentials): Promise<void> {
    const tokens = await api.post<TokenResponse>('/api/auth/login', credentials)
    setTokens(tokens)
    await fetchMe()
  }

  async function register(data: RegisterData): Promise<void> {
    await api.post('/api/auth/register', data)
    await login({ email: data.email, password: data.password })
  }

  async function fetchMe(): Promise<void> {
    if (!accessToken.value) return
    try {
      user.value = await api.get<User>('/api/auth/me')
    } catch {
      clearAuth()
    }
  }

  async function logout(): Promise<void> {
    clearAuth()
  }

  async function refresh(): Promise<boolean> {
    if (!refreshToken.value) return false
    try {
      const tokens = await api.post<TokenResponse>('/api/auth/refresh', {
        refresh_token: refreshToken.value,
      })
      setTokens(tokens)
      return true
    } catch {
      clearAuth()
      return false
    }
  }

  return {
    user,
    accessToken,
    isAuthenticated,
    isAdmin,
    isReviewer,
    login,
    register,
    logout,
    fetchMe,
    refresh,
    clearAuth,
  }
})
