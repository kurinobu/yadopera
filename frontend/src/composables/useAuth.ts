/**
 * 認証Composable
 */

import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import type { LoginRequest } from '@/types/auth'

export function useAuth() {
  const router = useRouter()
  const authStore = useAuthStore()

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
    try {
      await authApi.logout()
      authStore.logout()
      await router.push('/admin/login')
    } catch (error) {
      // エラーが発生してもログアウト処理は実行
      authStore.logout()
      await router.push('/admin/login')
    }
  }

  return {
    isAuthenticated,
    user,
    login,
    logout
  }
}


