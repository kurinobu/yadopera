/**
 * 認証状態管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Actions
  function setUser(userData: User | null) {
    user.value = userData
  }

  function setToken(tokenValue: string | null) {
    token.value = tokenValue
    if (tokenValue) {
      localStorage.setItem('auth_token', tokenValue)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  function login(userData: User, tokenValue: string) {
    setUser(userData)
    setToken(tokenValue)
  }

  function logout() {
    setUser(null)
    setToken(null)
  }

  function initAuth() {
    const storedToken = localStorage.getItem('auth_token')
    if (storedToken) {
      token.value = storedToken
      // TODO: トークンからユーザー情報を取得（Week 4で実装）
    }
  }

  return {
    user,
    token,
    isAuthenticated,
    setUser,
    setToken,
    login,
    logout,
    initAuth
  }
})

