<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- ヘッダー -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            YadOPERA
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            パスワードリセット / Password Reset
          </p>
        </div>

        <!-- 送信完了時 -->
        <div v-if="sent" class="text-center space-y-6">
          <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
            <p class="text-green-800 dark:text-green-200">
              送信しました。メールをご確認ください。
            </p>
            <p class="text-green-700 dark:text-green-300 text-sm mt-2">
              If an account exists for this email, you will receive a password reset link.
            </p>
          </div>
          <router-link
            to="/admin/login"
            class="inline-block text-blue-600 dark:text-blue-400 hover:underline"
          >
            ログインに戻る
          </router-link>
        </div>

        <!-- フォーム -->
        <form v-else @submit.prevent="handleSubmit" class="space-y-6">
          <Input
            v-model="email"
            type="email"
            label="メールアドレス / Email"
            placeholder="example@email.com"
            :required="true"
            :error="errorMessage"
            :disabled="isLoading"
          />

          <div
            v-if="errorMessage"
            class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <p class="text-sm text-red-600 dark:text-red-400">
              {{ errorMessage }}
            </p>
          </div>

          <button
            type="submit"
            :disabled="isLoading || !email.trim()"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              送信中...
            </span>
            <span v-else>
              リセット用メールを送信
            </span>
          </button>

          <div class="text-center">
            <router-link to="/admin/login" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">
              ログインに戻る
            </router-link>
          </div>
        </form>

        <div class="mt-6 text-center">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            © 2026 YadOPERA. All rights reserved.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import Input from '@/components/common/Input.vue'
import { authApi } from '@/api/auth'
import { isValidEmail } from '@/utils/validators'

const email = ref('')
const isLoading = ref(false)
const sent = ref(false)
const errorMessage = ref('')

const handleSubmit = async () => {
  errorMessage.value = ''
  const trimmed = email.value.trim()
  if (!trimmed) {
    errorMessage.value = 'メールアドレスを入力してください'
    return
  }
  if (!isValidEmail(trimmed)) {
    errorMessage.value = '有効なメールアドレスを入力してください'
    return
  }

  try {
    isLoading.value = true
    await authApi.requestPasswordReset({ email: trimmed })
    sent.value = true
  } catch (err: any) {
    const status = err.response?.status
    const detail = err.response?.data?.detail
    if (status === 429) {
      errorMessage.value = 'しばらく待ってから再度お試しください。'
    } else if (detail && typeof detail === 'string') {
      errorMessage.value = detail
    } else {
      errorMessage.value = '送信に失敗しました。しばらくしてから再度お試しください。'
    }
  } finally {
    isLoading.value = false
  }
}
</script>
