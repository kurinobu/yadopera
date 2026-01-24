/**
 * 開発者認証状態管理
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { developerApi } from '@/api/developer'
import { isDeveloperTokenExpired, logoutDeveloper } from '@/utils/developerAuth'

export const useDeveloperStore = defineStore('developer', () => {
  // State
  const token = ref<string | null>(null)
  const isAuthenticated = computed(() => {
    if (!token.value) {
      return false
    }
    // トークンの有効期限をチェック
    if (isDeveloperTokenExpired()) {
      // 期限切れの場合はログアウト
      logoutDeveloper()
      return false
    }
    return true
  })

  // Actions
  function setToken(tokenValue: string | null) {
    token.value = tokenValue
    try {
      if (tokenValue) {
        localStorage.setItem('developer_token', tokenValue)
      } else {
        localStorage.removeItem('developer_token')
      }
    } catch (error) {
      console.warn('Failed to access localStorage, token stored in memory only:', error)
    }
  }

  async function login(password: string) {
    try {
      const response = await developerApi.login(password)
      setToken(response.access_token)
      return response
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'ログインに失敗しました')
    }
  }

  function logout() {
    setToken(null)
  }

  function initAuth() {
    try {
      const storedToken = localStorage.getItem('developer_token')
      if (storedToken) {
        // トークンの有効期限をチェック
        if (isDeveloperTokenExpired()) {
          // 期限切れの場合は削除
          localStorage.removeItem('developer_token')
          token.value = null
        } else {
          token.value = storedToken
        }
      }
    } catch (error) {
      console.warn('Failed to access localStorage, continuing without auth:', error)
    }
  }

  return {
    token,
    isAuthenticated,
    setToken,
    login,
    logout,
    initAuth
  }
})

