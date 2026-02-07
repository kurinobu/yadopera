<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- 確認完了カード -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- ローディング状態 -->
        <div v-if="isVerifying" class="text-center">
          <div class="flex justify-center mb-6">
            <svg class="animate-spin h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            確認中...
          </h2>
          <p class="text-gray-600 dark:text-gray-400">
            メールアドレスを確認しています
          </p>
        </div>

        <!-- 成功状態 -->
        <div v-else-if="isSuccess" class="text-center">
          <!-- アイコン -->
          <div class="flex justify-center mb-6">
            <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
          </div>

          <!-- ヘッダー -->
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              メールアドレス確認完了！
            </h1>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Email Verification Successful
            </p>
          </div>

          <!-- メッセージ -->
          <div class="space-y-4 mb-6">
            <div class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-4">
              <p class="text-green-800 dark:text-green-200">
                アカウントの有効化が完了しました。<br>
                ログインしてYadOPERAをご利用いただけます。
              </p>
            </div>
            <p class="text-gray-700 dark:text-gray-300">
              確認済みメールアドレス：
            </p>
            <p class="text-blue-600 dark:text-blue-400 font-semibold text-center bg-blue-50 dark:bg-blue-900/20 py-2 px-4 rounded-md">
              {{ verifiedEmail }}
            </p>
          </div>

          <!-- ログインボタン -->
          <button
            @click="goToLogin"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            ログインページへ / Go to Login
          </button>
        </div>

        <!-- エラー状態 -->
        <div v-else class="text-center">
          <!-- アイコン -->
          <div class="flex justify-center mb-6">
            <div class="w-16 h-16 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          </div>

          <!-- ヘッダー -->
          <div class="mb-6">
            <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              確認に失敗しました
            </h1>
            <p class="text-gray-600 dark:text-gray-400 text-sm">
              Email Verification Failed
            </p>
          </div>

          <!-- エラーメッセージ -->
          <div class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-4 mb-6">
            <p class="text-red-600 dark:text-red-400">
              {{ errorMessage }}
            </p>
          </div>

          <!-- アクション -->
          <div class="space-y-3">
            <button
              @click="goToRegister"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              新規登録ページへ
            </button>
            <button
              @click="goToLogin"
              class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              ログインページへ
            </button>
          </div>
        </div>

        <!-- フッター -->
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const route = useRoute()
const router = useRouter()

const isVerifying = ref(true)
const isSuccess = ref(false)
const verifiedEmail = ref('')
const errorMessage = ref('')

const goToLogin = () => {
  router.push('/admin/login')
}

const goToRegister = () => {
  router.push('/admin/register')
}

onMounted(async () => {
  const token = route.query.token as string
  
  if (!token) {
    isVerifying.value = false
    errorMessage.value = '確認トークンが指定されていません。'
    return
  }

  try {
    const response = await authApi.verifyEmail({ token })
    verifiedEmail.value = response.email
    isSuccess.value = true
  } catch (error: any) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = 'メールアドレスの確認に失敗しました。トークンが無効または期限切れの可能性があります。'
    }
  } finally {
    isVerifying.value = false
  }
})
</script>

