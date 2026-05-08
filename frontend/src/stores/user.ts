import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { post, get } from '@/api/request'
import { logout as logoutApi } from '@/api/auth'
import type { ApiResponse } from '@/types/api'

interface LoginResponse {
  token: string
  user: User
}

export const useUserStore = defineStore('user', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  function setToken(newToken: string) {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  function setUser(newUser: User) {
    user.value = newUser
  }

  async function login(username: string, password: string) {
    const res = await post<ApiResponse<LoginResponse>>('/v1/auth/login', { username, password })
    setToken(res.data.token)
    setUser(res.data.user)
  }

  async function fetchUser() {
    if (!token.value) return
    try {
      const res = await get<ApiResponse<User>>('/v1/auth/me')
      setUser(res.data)
    } catch {
      logout()
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch {
      // Ignore errors — clear local state regardless
    }
    token.value = null
    user.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    setToken,
    setUser,
    login,
    fetchUser,
    logout
  }
})
