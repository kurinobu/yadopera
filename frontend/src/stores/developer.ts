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
    
    try {
      // トークンの有効期限をチェック
      if (isDeveloperTokenExpired()) {
        // 期限切れの場合はログアウト
        console.info('Developer token expired, logging out')
        logoutDeveloper()
        return false
      }
      return true
    } catch (error) {
      // エラーが発生した場合は認証失敗とみなす
      console.warn('Error checking developer authentication:', error)
      return false
    }
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
      // ブラウザ環境でない場合は何もしない
      if (typeof window === 'undefined' || typeof localStorage === 'undefined') {
        console.warn('Cannot initialize auth: not in browser environment')
        return
      }

      const storedToken = localStorage.getItem('developer_token')
      if (storedToken) {
        try {
          // トークンの有効期限をチェック
          if (isDeveloperTokenExpired()) {
            // 期限切れの場合は削除
            console.info('Stored developer token expired, removing')
            localStorage.removeItem('developer_token')
            token.value = null
          } else {
            console.info('Developer token loaded from storage')
            token.value = storedToken
          }
        } catch (tokenError) {
          console.warn('Error checking stored token, removing:', tokenError)
          localStorage.removeItem('developer_token')
          token.value = null
        }
      }
    } catch (error) {
      console.warn('Failed to access localStorage, continuing without auth:', error)
      token.value = null
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

