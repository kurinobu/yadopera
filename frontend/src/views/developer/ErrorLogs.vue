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
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- エラーレベルフィルター（既存） -->
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
        
        <!-- 施設フィルター（修正: 施設名ドロップダウンに変更） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            施設
          </label>
          <select
            v-model="filters.facility_id"
            :disabled="loadingFacilities"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <option :value="undefined">すべて</option>
            <option
              v-for="facility in facilities"
              :key="facility.id"
              :value="facility.id"
            >
              {{ facility.name }} (ID: {{ facility.id }})
            </option>
          </select>
        </div>
        
        <!-- 開始日時フィルター（追加） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            開始日時
          </label>
          <input
            v-model="filters.start_date"
            type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        
        <!-- 終了日時フィルター（追加） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            終了日時
          </label>
          <input
            v-model="filters.end_date"
            type="datetime-local"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
        </div>
        
        <!-- バリデーションエラー表示（追加） -->
        <div v-if="dateRangeError" class="md:col-span-2 lg:col-span-3">
          <p class="text-sm text-red-600 dark:text-red-400">{{ dateRangeError }}</p>
        </div>
        
        <!-- フィルター適用ボタン（既存） -->
        <div class="flex items-end">
          <button
            @click="applyFilters"
            class="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg"
          >
            フィルター適用
          </button>
        </div>
        
        <!-- クリアボタン（既存） -->
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
      <div class="overflow-x-auto">
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
      </div>

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
import type { ErrorLog, PaginationInfo, FacilitySummary } from '@/types/developer'

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
  facility_id: undefined as number | undefined,
  start_date: '' as string,  // 開始日時（YYYY-MM-DDTHH:mm形式）
  end_date: '' as string     // 終了日時（YYYY-MM-DDTHH:mm形式）
})

// 施設一覧を保持
const facilities = ref<FacilitySummary[]>([])
const loadingFacilities = ref(false)

// 日付範囲のバリデーションエラー
const dateRangeError = ref('')

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
    // 追加: 日付範囲パラメータ
    if (filters.value.start_date) {
      // datetime-local形式（YYYY-MM-DDTHH:mm）をISO 8601形式に変換
      // JST（Asia/Tokyo）として解釈し、UTCに変換
      const startDate = new Date(filters.value.start_date)
      // JSTオフセット（+09:00）を適用
      const jstOffset = 9 * 60 * 60 * 1000 // 9時間をミリ秒に変換
      const utcDate = new Date(startDate.getTime() - jstOffset)
      params.start_date = utcDate.toISOString()
    }
    if (filters.value.end_date) {
      // datetime-local形式（YYYY-MM-DDTHH:mm）をISO 8601形式に変換
      // JST（Asia/Tokyo）として解釈し、UTCに変換
      const endDate = new Date(filters.value.end_date)
      // JSTオフセット（+09:00）を適用
      const jstOffset = 9 * 60 * 60 * 1000 // 9時間をミリ秒に変換
      const utcDate = new Date(endDate.getTime() - jstOffset)
      // 終了日時はその日の23:59:59までを含めるため、1日分のミリ秒を追加
      const endOfDay = new Date(utcDate.getTime() + 24 * 60 * 60 * 1000 - 1)
      params.end_date = endOfDay.toISOString()
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
  // バリデーション
  if (!validateDateRange()) {
    return
  }
  
  pagination.value.page = 1
  fetchErrors()
}

const clearFilters = () => {
  filters.value = {
    level: '',
    facility_id: undefined,
    start_date: '',
    end_date: ''
  }
  dateRangeError.value = ''
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

// 日付範囲のバリデーション
const validateDateRange = (): boolean => {
  dateRangeError.value = ''
  
  if (filters.value.start_date && filters.value.end_date) {
    const startDate = new Date(filters.value.start_date)
    const endDate = new Date(filters.value.end_date)
    
    if (startDate > endDate) {
      dateRangeError.value = '開始日時は終了日時より前である必要があります'
      return false
    }
  }
  
  return true
}

// 施設一覧を取得
const fetchFacilities = async () => {
  try {
    loadingFacilities.value = true
    const response = await developerApi.getFacilities()
    facilities.value = response.facilities
  } catch (err: any) {
    console.error('Failed to fetch facilities:', err)
    // エラー時は施設一覧を空にする（フィルターは使用不可になるが、エラーログ表示は継続）
  } finally {
    loadingFacilities.value = false
  }
}

onMounted(() => {
  fetchFacilities()
  fetchErrors()
})
</script>

<style scoped>
/* Component styles */
</style>

