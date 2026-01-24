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
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        エラーログ
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        システムで発生したエラーの一覧
      </p>
    </div>

    <!-- フィルター -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            エラーレベル
          </label>
          <select
            v-model="filters.level"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">すべて</option>
            <option value="critical">Critical</option>
            <option value="error">Error</option>
            <option value="warning">Warning</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            施設ID
          </label>
          <input
            v-model.number="filters.facility_id"
            type="number"
            placeholder="施設ID"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="applyFilters"
            class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg"
          >
            フィルター適用
          </button>
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg"
          >
            クリア
          </button>
        </div>
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

    <!-- エラーログテーブル -->
    <div v-else-if="errorLogs.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              ID
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              レベル
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              コード
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              メッセージ
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              リクエストパス
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              施設
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              発生時刻
            </th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              操作
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr
            v-for="errorLog in errorLogs"
            :key="errorLog.id"
            class="hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ errorLog.id }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span
                :class="{
                  'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400': errorLog.level === 'critical',
                  'bg-orange-100 text-orange-800 dark:bg-orange-900/20 dark:text-orange-400': errorLog.level === 'error',
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400': errorLog.level === 'warning'
                }"
                class="px-2 py-1 rounded text-xs font-medium"
              >
                {{ errorLog.level.toUpperCase() }}
              </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-500 dark:text-gray-400">
              {{ errorLog.code }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white max-w-md truncate">
              {{ errorLog.message }}
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">
              {{ errorLog.request_path || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ errorLog.facility_name || '-' }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(errorLog.created_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button
                @click="viewDetail(errorLog.id)"
                class="text-blue-600 hover:text-blue-700 dark:text-blue-400"
              >
                詳細
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- ページネーション -->
      <div v-if="pagination.total_pages > 1" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ pagination.page }} / {{ pagination.total_pages }} ページ
          (全 {{ pagination.total }} 件)
        </div>
        <div class="flex gap-2">
          <button
            @click="changePage(pagination.page - 1)"
            :disabled="pagination.page <= 1"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50"
          >
            前へ
          </button>
          <button
            @click="changePage(pagination.page + 1)"
            :disabled="pagination.page >= pagination.total_pages"
            class="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded disabled:opacity-50"
          >
            次へ
          </button>
        </div>
      </div>
    </div>

    <!-- データなし -->
    <div v-else class="text-center py-12">
      <p class="text-gray-500 dark:text-gray-400">エラーログがありません</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { developerApi } from '@/api/developer'
import type { ErrorLog, PaginationInfo } from '@/types/developer'

const router = useRouter()

const loading = ref(true)
const error = ref('')
const errorLogs = ref<ErrorLog[]>([])
const pagination = ref<PaginationInfo>({
  page: 1,
  per_page: 50,
  total: 0,
  total_pages: 0
})

const filters = ref({
  level: '',
  facility_id: undefined as number | undefined
})

const fetchErrors = async () => {
  try {
    loading.value = true
    error.value = ''

    const params: any = {
      page: pagination.value.page,
      per_page: pagination.value.per_page
    }

    if (filters.value.level) {
      params.level = filters.value.level
    }
    if (filters.value.facility_id) {
      params.facility_id = filters.value.facility_id
    }

    const response = await developerApi.getErrors(params)
    errorLogs.value = response.errors
    pagination.value = response.pagination
  } catch (err: any) {
    error.value = err.message || 'エラーログの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  pagination.value.page = 1
  fetchErrors()
}

const clearFilters = () => {
  filters.value = {
    level: '',
    facility_id: undefined
  }
  pagination.value.page = 1
  fetchErrors()
}

const changePage = (page: number) => {
  pagination.value.page = page
  fetchErrors()
}

const viewDetail = (errorId: number) => {
  router.push({ name: 'DeveloperErrorLogDetail', params: { errorId } })
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchErrors()
})
</script>

<style scoped>
/* Component styles */
</style>

