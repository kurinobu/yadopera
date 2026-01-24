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
            開発者管理ページ / Developer Management
          </p>
        </div>

        <!-- エラーメッセージ -->
        <div
          v-if="error"
          class="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-800 dark:text-red-200 text-sm"
        >
          {{ error }}
        </div>

        <!-- ログインフォーム -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              パスワード / Password
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              :disabled="isLoading"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
              placeholder="開発者パスワードを入力"
            />
          </div>

          <button
            type="submit"
            :disabled="isLoading || !password"
            class="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <span v-if="isLoading">ログイン中...</span>
            <span v-else>ログイン / Login</span>
          </button>
        </form>

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
import { useRouter } from 'vue-router'
import { useDeveloperStore } from '@/stores/developer'

const router = useRouter()
const developerStore = useDeveloperStore()

const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  try {
    error.value = ''
    isLoading.value = true
    
    await developerStore.login(password.value)
    
    // ログイン成功後、ダッシュボードにリダイレクト
    router.push({ name: 'DeveloperDashboard' })
  } catch (err: any) {
    error.value = err.message || 'ログインに失敗しました。パスワードを確認してください。'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* Component styles */
</style>

