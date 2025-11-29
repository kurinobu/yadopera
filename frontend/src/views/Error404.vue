<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-12">
    <div class="text-center">
      <div class="mb-8">
        <h1 class="text-9xl font-bold text-gray-300 dark:text-gray-700">
          404
        </h1>
      </div>
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
        ページが見つかりません
      </h2>
      <p class="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-md mx-auto">
        お探しのページは存在しないか、移動された可能性があります。
      </p>
      <div class="flex items-center justify-center space-x-4">
        <router-link
          to="/"
          class="px-6 py-3 text-base font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
        >
          ホームに戻る
        </router-link>
        <button
          @click="handleGoBack"
          class="px-6 py-3 text-base font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
        >
          前のページに戻る
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const handleGoBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/')
  }
}
</script>

<style scoped>
/* Component styles */
</style>

