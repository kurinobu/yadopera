<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- 確認待ちカード -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- アイコン -->
        <div class="flex justify-center mb-6">
          <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
            <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        <!-- ヘッダー -->
        <div class="text-center mb-6">
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            確認メールを送信しました
          </h1>
          <p class="text-gray-600 dark:text-gray-400 text-sm">
            Email Verification Sent
          </p>
        </div>

        <!-- メッセージ -->
        <div class="space-y-4 mb-6">
          <p class="text-gray-700 dark:text-gray-300">
            {{ facilityName }} 様
          </p>
          <p class="text-gray-700 dark:text-gray-300">
            以下のメールアドレスに確認メールを送信しました：
          </p>
          <p class="text-blue-600 dark:text-blue-400 font-semibold text-center bg-blue-50 dark:bg-blue-900/20 py-2 px-4 rounded-md">
            {{ email }}
          </p>
          <p class="text-gray-700 dark:text-gray-300">
            メール内のリンクをクリックして、アカウントを有効化してください。
          </p>
          <div class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-md p-3">
            <p class="text-yellow-800 dark:text-yellow-200 text-sm">
              <strong>注意:</strong> 確認リンクは24時間後に無効になります。
            </p>
          </div>
        </div>

        <!-- 再送信ボタン -->
        <div class="space-y-4">
          <button
            @click="resendEmail"
            :disabled="isResending || cooldownRemaining > 0"
            class="w-full flex justify-center py-2 px-4 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isResending" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-700 dark:text-gray-300" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              送信中...
            </span>
            <span v-else-if="cooldownRemaining > 0">
              再送信まで {{ cooldownRemaining }}秒
            </span>
            <span v-else>
              確認メールを再送信
            </span>
          </button>

          <!-- 成功メッセージ -->
          <div v-if="resendSuccess" class="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md p-3">
            <p class="text-green-600 dark:text-green-400 text-sm">
              確認メールを再送信しました。メールをご確認ください。
            </p>
          </div>

          <!-- 🟡 エラーメッセージ（強化） -->
          <div v-if="resendError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
            <p class="text-red-600 dark:text-red-400 text-sm">
              {{ resendError }}
            </p>
          </div>
        </div>

        <!-- ログインページへのリンク -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            既に確認済みですか？
            <router-link to="/admin/login" class="font-medium text-blue-600 hover:text-blue-500 dark:text-blue-400">
              ログイン / Login
            </router-link>
          </p>
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
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { authApi } from '@/api/auth'

const route = useRoute()

const email = ref(route.query.email as string || '')
const facilityName = ref(route.query.facility_name as string || '')
const isResending = ref(false)
const resendSuccess = ref(false)
const resendError = ref('')
const cooldownRemaining = ref(0)
let cooldownTimer: number | null = null

const resendEmail = async () => {
  try {
    isResending.value = true
    resendSuccess.value = false
    resendError.value = ''

    await authApi.resendVerification({
      email: email.value
    })

    resendSuccess.value = true
    
    // クールダウン開始（60秒）
    cooldownRemaining.value = 60
    cooldownTimer = window.setInterval(() => {
      cooldownRemaining.value--
      if (cooldownRemaining.value <= 0 && cooldownTimer) {
        clearInterval(cooldownTimer)
        cooldownTimer = null
      }
    }, 1000)
  } catch (error: any) {
    // 🟡 HTTPステータスコード別のエラー処理（強化）
    if (error.response) {
      // サーバーからのエラーレスポンス
      const status = error.response.status
      const detail = error.response.data?.detail
      
      if (status === 429) {
        // レート制限
        resendError.value = 'しばらく時間をおいてから再度お試しください。（60秒）'
      } else if (detail) {
        resendError.value = detail
      } else {
        resendError.value = '再送信に失敗しました。'
      }
    } else if (error.request) {
      // ネットワークエラー（リクエストは送信されたがレスポンスなし）
      resendError.value = 'ネットワークエラーが発生しました。インターネット接続を確認してください。'
    } else {
      // その他のエラー
      resendError.value = '予期しないエラーが発生しました。'
    }
  } finally {
    isResending.value = false
  }
}

onMounted(() => {
  // メールアドレスがない場合は登録ページへリダイレクト
  if (!email.value) {
    window.location.href = '/admin/register'
  }
})

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
  }
})
</script>

