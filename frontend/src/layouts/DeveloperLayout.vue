<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- ヘッダー -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">
              YadOPERA 開発者管理
            </h1>
          </div>
          <div class="flex items-center gap-4">
            <router-link
              :to="{ name: 'DeveloperDashboard' }"
              class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              ダッシュボード
            </router-link>
            <router-link
              :to="{ name: 'DeveloperErrorLogs' }"
              class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              エラーログ
            </router-link>
            <button
              @click="handleLogout"
              class="text-sm text-red-600 hover:text-red-700 dark:text-red-400"
            >
              ログアウト
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- メインコンテンツ -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useDeveloperStore } from '@/stores/developer'

const router = useRouter()
const developerStore = useDeveloperStore()

const handleLogout = () => {
  developerStore.logout()
  router.push({ name: 'DeveloperLogin' })
}
</script>

<style scoped>
/* Component styles */
</style>

