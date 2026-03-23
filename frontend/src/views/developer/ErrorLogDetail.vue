<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <div>
        <button
          @click="$router.push({ name: 'DeveloperErrorLogs' })"
          class="mb-2 text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400"
        >
          ← エラーログ一覧に戻る
        </button>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          エラーログ詳細
        </h1>
      </div>
    </div>

    <!-- ローディング表示 -->
    <div v-if="loading" class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">読み込み中...</p>
    </div>

    <!-- エラー表示 -->
    <div
      v-else-if="error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <!-- エラーログ詳細 -->
    <div v-else-if="errorDetail" class="space-y-6">
      <!-- 基本情報 -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">基本情報</h2>
        <dl class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">ID</dt>
            <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ errorDetail.id }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">レベル</dt>
            <dd class="mt-1">
              <span
                :class="{
                  'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': errorDetail.level === 'critical',
                  'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400': errorDetail.level === 'error',
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': errorDetail.level === 'warning'
                }"
                class="px-2 py-1 rounded text-xs font-medium"
              >
                {{ errorDetail.level.toUpperCase() }}
              </span>
            </dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">エラーコード</dt>
            <dd class="mt-1 text-sm font-mono text-gray-900 dark:text-white">{{ errorDetail.code }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">発生時刻</dt>
            <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ formatDate(errorDetail.created_at) }}</dd>
          </div>
          <div v-if="errorDetail.request_method">
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">HTTPメソッド</dt>
            <dd class="mt-1 text-sm text-gray-900 dark:text-white">{{ errorDetail.request_method }}</dd>
          </div>
          <div v-if="errorDetail.request_path">
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">リクエストパス</dt>
            <dd class="mt-1 text-sm font-mono text-gray-900 dark:text-white">{{ errorDetail.request_path }}</dd>
          </div>
          <div v-if="errorDetail.facility">
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">施設</dt>
            <dd class="mt-1 text-sm text-gray-900 dark:text-white">
              {{ errorDetail.facility.name }} (ID: {{ errorDetail.facility.id }})
            </dd>
          </div>
          <div v-if="errorDetail.user">
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">ユーザー</dt>
            <dd class="mt-1 text-sm text-gray-900 dark:text-white">
              {{ errorDetail.user.email }} (ID: {{ errorDetail.user.id }})
            </dd>
          </div>
          <div v-if="errorDetail.ip_address">
            <dt class="text-sm font-medium text-gray-500 dark:text-gray-400">IPアドレス</dt>
            <dd class="mt-1 text-sm font-mono text-gray-900 dark:text-white">{{ errorDetail.ip_address }}</dd>
          </div>
        </dl>
      </div>

      <!-- エラーメッセージ -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">エラーメッセージ</h2>
        <pre class="whitespace-pre-wrap text-sm text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-900 p-4 rounded border border-gray-200 dark:border-gray-700">{{ errorDetail.message }}</pre>
      </div>

      <!-- スタックトレース -->
      <div v-if="errorDetail.stack_trace" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">スタックトレース</h2>
        <pre class="whitespace-pre-wrap text-xs text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-900 p-4 rounded border border-gray-200 dark:border-gray-700 overflow-x-auto">{{ errorDetail.stack_trace }}</pre>
      </div>

      <!-- User-Agent -->
      <div v-if="errorDetail.user_agent" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-4">User-Agent</h2>
        <p class="text-sm font-mono text-gray-900 dark:text-white bg-gray-50 dark:bg-gray-900 p-4 rounded border border-gray-200 dark:border-gray-700">
          {{ errorDetail.user_agent }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { developerApi } from '@/api/developer'
import type { ErrorLogDetail } from '@/types/developer'

const route = useRoute()

const loading = ref(true)
const error = ref('')
const errorDetail = ref<ErrorLogDetail | null>(null)

const fetchErrorDetail = async () => {
  try {
    loading.value = true
    error.value = ''

    const errorId = parseInt(route.params.errorId as string)
    if (isNaN(errorId)) {
      throw new Error('Invalid error ID')
    }

    const data = await developerApi.getErrorDetail(errorId)
    errorDetail.value = data
  } catch (err: any) {
    error.value = err.message || 'エラーログの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
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
  fetchErrorDetail()
})
</script>

<style scoped>
/* Component styles */
</style>

