<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="w-full max-w-md">
      <!-- 登録カード -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <!-- ヘッダー -->
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            YadOPERA
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            新規施設登録 / Facility Registration
          </p>
        </div>

        <!-- 登録フォーム -->
        <form @submit.prevent="handleRegister" class="space-y-6">
          <!-- 施設名 -->
          <div>
            <label for="facility_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              施設名 / Facility Name
            </label>
            <input
              id="facility_name"
              v-model="form.facility_name"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="例: 東京ゲストハウス"
            />
          </div>

          <!-- メールアドレス -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              メールアドレス / Email
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="admin@example.com"
            />
          </div>

          <!-- パスワード -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              パスワード / Password
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              minlength="8"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="8文字以上"
            />
          </div>

          <!-- 料金プラン -->
          <div>
            <label for="subscription_plan" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              料金プラン / Subscription Plan
            </label>
            <select
              id="subscription_plan"
              v-model="form.subscription_plan"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            >
              <option value="free">Free</option>
              <option value="mini">Mini</option>
              <option value="small">Small (推奨)</option>
              <option value="standard">Standard</option>
              <option value="premium">Premium</option>
            </select>
          </div>

          <!-- エラーメッセージ -->
          <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md p-3">
            <p class="text-red-600 dark:text-red-400 text-sm">
              {{ errorMessage }}
            </p>
          </div>

          <!-- 登録ボタン -->
          <button
            type="submit"
            :disabled="isLoading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isLoading" class="flex items-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              登録中...
            </span>
            <span v-else>
              施設を登録 / Register Facility
            </span>
          </button>
        </form>

        <!-- ログインページへのリンク -->
        <div class="mt-6 text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            既にアカウントをお持ちですか？
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '@/api/auth'

const router = useRouter()

const form = reactive({
  email: '',
  password: '',
  facility_name: '',
  subscription_plan: 'small'
})

const isLoading = ref(false)
const errorMessage = ref('')

const handleRegister = async () => {
  try {
    isLoading.value = true
    errorMessage.value = ''

    const response = await authApi.register({
      email: form.email,
      password: form.password,
      facility_name: form.facility_name,
      subscription_plan: form.subscription_plan
    })

    // ★成功時は確認メール送信完了画面へ遷移
    router.push({
      name: 'EmailVerificationPending',
      query: {
        email: form.email,
        facility_name: form.facility_name
      }
    })
  } catch (error: any) {
    if (error.response?.data?.detail) {
      errorMessage.value = error.response.data.detail
    } else {
      errorMessage.value = '登録に失敗しました。入力内容を確認してください。'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Component styles */
</style>