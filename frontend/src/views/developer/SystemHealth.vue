<template>
  <div class="space-y-6">
    <!-- 戻るボタン -->
    <button
      @click="$router.push({ name: 'DeveloperDashboard' })"
      class="mb-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
    >
      ← ダッシュボードに戻る
    </button>

    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          システムヘルスチェック
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          データベース、Redis、OpenAI APIの接続状態とレスポンスタイムを確認
        </p>
      </div>
      <button
        @click="refreshHealth"
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? '更新中...' : '更新' }}
      </button>
    </div>

    <!-- ローディング状態 -->
    <div v-if="loading && !health" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 dark:border-white"></div>
      <p class="mt-2 text-gray-600 dark:text-gray-400">システムヘルスチェック中...</p>
    </div>

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
          </svg>
        </div>
        <div class="ml-3">
          <h3 class="text-sm font-medium text-red-800 dark:text-red-200">
            システムヘルスチェック取得エラー
          </h3>
          <div class="mt-2 text-sm text-red-700 dark:text-red-300">
            {{ error }}
          </div>
        </div>
      </div>
    </div>

    <!-- システムヘルス情報 -->
    <div v-else-if="health" class="grid gap-6 md:grid-cols-3">
      <!-- データベース -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            データベース
          </h3>
          <div class="flex items-center">
            <div
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': health.database.status === 'ok',
                'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': health.database.status === 'error'
              }"
              class="px-2 py-1 rounded text-xs font-semibold"
            >
              {{ health.database.status === 'ok' ? '正常' : 'エラー' }}
            </div>
          </div>
        </div>
        <div class="space-y-3">
          <div v-if="health.database.response_time_ms" class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">応答時間:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ health.database.response_time_ms.toFixed(2) }} ms
            </span>
          </div>
          <div v-if="health.database.error" class="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded p-3">
            <p class="text-sm text-red-600 dark:text-red-400 font-mono">
              {{ health.database.error }}
            </p>
          </div>
        </div>
      </div>

      <!-- Redis -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            Redis
          </h3>
          <div class="flex items-center">
            <div
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': health.redis.status === 'ok',
                'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': health.redis.status === 'error'
              }"
              class="px-2 py-1 rounded text-xs font-semibold"
            >
              {{ health.redis.status === 'ok' ? '正常' : 'エラー' }}
            </div>
          </div>
        </div>
        <div class="space-y-3">
          <div v-if="health.redis.response_time_ms" class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">応答時間:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ health.redis.response_time_ms.toFixed(2) }} ms
            </span>
          </div>
          <div v-if="health.redis.error" class="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded p-3">
            <p class="text-sm text-red-600 dark:text-red-400 font-mono">
              {{ health.redis.error }}
            </p>
          </div>
        </div>
      </div>

      <!-- OpenAI API -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            OpenAI API
          </h3>
          <div class="flex items-center">
            <div
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400': health.openai_api?.status === 'ok',
                'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': health.openai_api?.status === 'not_configured',
                'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': health.openai_api?.status === 'error'
              }"
              class="px-2 py-1 rounded text-xs font-semibold"
            >
              {{ getOpenAIStatusText(health.openai_api?.status) }}
            </div>
          </div>
        </div>
        <div class="space-y-3">
          <div v-if="health.openai_api?.response_time_ms !== undefined && health.openai_api?.response_time_ms !== null" class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">応答時間:</span>
            <span class="text-sm font-mono text-gray-900 dark:text-white">
              {{ health.openai_api.response_time_ms.toFixed(2) }} ms
            </span>
          </div>
          <div v-else-if="health.openai_api?.status === 'ok'" class="flex items-center justify-between">
            <span class="text-sm text-gray-600 dark:text-gray-400">設定状態:</span>
            <span class="text-sm text-gray-900 dark:text-white">
              設定済み
            </span>
          </div>
          <div v-if="health.openai_api?.error" class="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-800 rounded p-3">
            <p class="text-sm text-red-600 dark:text-red-400 font-mono">
              {{ health.openai_api.error }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 最終更新時刻 -->
    <div v-if="health && lastUpdated" class="text-center text-sm text-gray-500 dark:text-gray-400">
      最終更新: {{ formatDate(lastUpdated) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { developerApi } from '@/api/developer'
import type { SystemHealthResponse } from '@/types/developer'

const health = ref<SystemHealthResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdated = ref<Date | null>(null)

const fetchHealth = async () => {
  loading.value = true
  error.value = null
  try {
    health.value = await developerApi.getSystemHealth()
    lastUpdated.value = new Date()
  } catch (err: any) {
    error.value = err.response?.data?.error?.message || err.message || 'システムヘルスチェックの取得に失敗しました'
    console.error('Failed to fetch system health:', err)
  } finally {
    loading.value = false
  }
}

const refreshHealth = () => {
  fetchHealth()
}

const getOpenAIStatusText = (status: string | undefined): string => {
  switch (status) {
    case 'ok':
      return '正常'
    case 'not_configured':
      return '未設定'
    case 'error':
      return 'エラー'
    default:
      return '不明'
  }
}

const formatDate = (date: Date) => {
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

onMounted(() => {
  fetchHealth()
})
</script>

<style scoped>
/* Component styles */
</style>
