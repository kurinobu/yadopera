/**
 * 認証Composable
 */

import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import type { LoginRequest } from '@/types/auth'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()
  const isLoggingOut = ref(false)

  const isAuthenticated = computed(() => authStore.isAuthenticated)
  const user = computed(() => authStore.user)

  async function login(loginData: LoginRequest) {
    try {
      const response = await authApi.login(loginData)
      authStore.login(response.user, response.access_token)
      await router.push('/admin/dashboard')
      return response
    } catch (error) {
      throw error
    }
  }

  async function logout() {
    // ログアウト処理中フラグを設定（二重実行を防ぐ）
    if (isLoggingOut.value) {
      console.warn('Logout already in progress')
      return
    }
    isLoggingOut.value = true

    try {
      // トークンが存在する場合のみAPIを呼び出し
      if (authStore.token) {
        try {
          await authApi.logout()
        } catch (error) {
          // エラーが発生してもログアウト処理は続行
          console.warn('Logout API error (ignored):', error)
        }
      }

      // クライアント側でトークンを削除（必ず実行）
      authStore.logout()

      // ログイン画面にリダイレクト
      await router.push('/admin/login')
    } catch (error) {
      // 予期しないエラーが発生した場合でもログアウト処理は実行
      console.error('Unexpected logout error:', error)
      authStore.logout()
      await router.push('/admin/login')
    } finally {
      isLoggingOut.value = false
    }
  }

  return {
    isAuthenticated,
    user,
    login,
    logout
  }
}


