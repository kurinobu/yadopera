<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- ログインカード -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- ヘッダー -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            YadOPERA
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            管理画面にログイン / Admin Login
          </p>
        </div>

        <!-- ログインフォーム -->
        <LoginForm
          ref="loginFormRef"
          :is-loading="isLoading"
          @submit="handleLogin"
        />

        <!-- パスワードを忘れた場合 -->
        <div class="mt-4 text-center">
          <router-link
            to="/admin/password-reset"
            class="text-sm text-blue-600 dark:text-blue-400 hover:underline"
          >
            パスワードを忘れた場合はこちら
          </router-link>
        </div>

        <!-- フッター -->
        <div class="mt-6 text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            © 2024 YadOPERA. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth'
import LoginForm from '@/components/admin/LoginForm.vue'
import { getApiErrorMessage } from '@/utils/errorHandler'

const { login } = useAuth()

const loginFormRef = ref<InstanceType<typeof LoginForm> | null>(null)
const isLoading = ref(false)

const handleLogin = async (email: string, password: string) => {
  try {
    isLoading.value = true
    
    // エラーをクリア
    if (loginFormRef.value) {
      loginFormRef.value.clearErrors()
    }

    await login({ email, password })
  } catch (error: unknown) {
    const apiMsg = getApiErrorMessage(error)
    if (loginFormRef.value) {
      loginFormRef.value.setError(
        apiMsg ?? 'ログインに失敗しました。メールアドレスとパスワードを確認してください。'
      )
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Component styles */
</style>

