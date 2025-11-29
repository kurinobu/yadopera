<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          夜間対応キュー
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          翌朝対応が必要な質問一覧
        </p>
      </div>
      <ProcessButton
        :loading="isProcessing"
        loading-text="処理中..."
        @click="handleProcess"
      >
        手動実行
      </ProcessButton>
    </div>

    <!-- 説明 -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-start">
        <svg
          class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
            夜間対応キューについて
          </h3>
          <p class="text-sm text-blue-700 dark:text-blue-300">
            夜間（22:00-8:00）にエスカレーションされた質問は、自動的に翌朝8:00にスタッフへ通知されます。
            MVP期間中は「手動実行」ボタンで通知処理を実行できます。
          </p>
        </div>
      </div>
    </div>

    <!-- 統計情報 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
              未対応
            </p>
            <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {{ pendingCount }}
            </p>
          </div>
          <div class="p-3 bg-yellow-100 dark:bg-yellow-900 rounded-full">
            <svg
              class="w-6 h-6 text-yellow-600 dark:text-yellow-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
              対応済み
            </p>
            <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {{ resolvedCount }}
            </p>
          </div>
          <div class="p-3 bg-green-100 dark:bg-green-900 rounded-full">
            <svg
              class="w-6 h-6 text-green-600 dark:text-green-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">
              合計
            </p>
            <p class="mt-1 text-2xl font-bold text-gray-900 dark:text-white">
              {{ totalCount }}
            </p>
          </div>
          <div class="p-3 bg-blue-100 dark:bg-blue-900 rounded-full">
            <svg
              class="w-6 h-6 text-blue-600 dark:text-blue-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- ローディング表示 -->
    <Loading v-if="loading" />

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchOvernightQueue"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- 夜間対応キューリスト -->
    <OvernightQueueList
      v-else
      :queue="queue"
      @resolve="handleResolve"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import OvernightQueueList from '@/components/admin/OvernightQueueList.vue'
import ProcessButton from '@/components/admin/ProcessButton.vue'
import Loading from '@/components/common/Loading.vue'
import { overnightQueueApi } from '@/api/overnightQueue'
import type { OvernightQueue } from '@/types/dashboard'

// データ状態
const loading = ref(true)
const error = ref<string | null>(null)
const queueData = ref<{ queues: OvernightQueue[]; total: number; pending_count: number; resolved_count: number } | null>(null)

// データ取得
const fetchOvernightQueue = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await overnightQueueApi.getOvernightQueue(false) // 未解決のみ
    queueData.value = data
  } catch (err: any) {
    console.error('Failed to fetch overnight queue:', err)
    error.value = err.response?.data?.detail || '夜間対応キューの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

// コンポーネントマウント時にデータ取得
onMounted(() => {
  fetchOvernightQueue()
})

// 計算プロパティ
const queue = computed(() => queueData.value?.queues || [])
const pendingCount = computed(() => queueData.value?.pending_count || 0)
const resolvedCount = computed(() => queueData.value?.resolved_count || 0)
const totalCount = computed(() => queueData.value?.total || 0)

// モックデータ（Week 4でAPI連携に置き換え）
const mockQueue: OvernightQueue[] = [
  {
    id: 1,
    facility_id: 1,
    escalation_id: 1,
    guest_message: 'Late checkout possible?',
    language: 'en',
    scheduled_notify_at: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(), // 8時間後
    notified_at: null,
    resolved_at: null,
    resolved_by: null,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2時間前
  },
  {
    id: 2,
    facility_id: 1,
    escalation_id: 2,
    guest_message: 'タオルはどこにありますか？',
    language: 'ja',
    scheduled_notify_at: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
    notified_at: null,
    resolved_at: null,
    resolved_by: null,
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString() // 1時間前
  },
  {
    id: 3,
    facility_id: 1,
    escalation_id: 3,
    guest_message: 'Where can I buy breakfast?',
    language: 'en',
    scheduled_notify_at: new Date(Date.now() + 8 * 60 * 60 * 1000).toISOString(),
    notified_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30分前に通知済み
    resolved_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(), // 10分前に解決済み
    resolved_by: 1,
    created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString() // 3時間前
  }
]

const isProcessing = ref(false)

const handleProcess = async () => {
  if (isProcessing.value) return
  
  try {
    isProcessing.value = true
    const result = await overnightQueueApi.processNotifications()
    
    if (result.processed_count > 0) {
      alert(`${result.processed_count}件の質問をスタッフへ通知しました。`)
      // キュー一覧を再取得
      await fetchOvernightQueue()
    } else {
      alert('処理対象の質問はありません。')
    }
  } catch (err: any) {
    console.error('Process error:', err)
    alert(err.response?.data?.detail || '処理中にエラーが発生しました。')
  } finally {
    isProcessing.value = false
  }
}

const handleResolve = async (item: OvernightQueue) => {
  // TODO: 対応済みマークAPIはPhase 2で実装予定
  // 現時点では手動で対応済みにする機能は未実装
  if (confirm('この質問を対応済みにマークしますか？\n（現時点では手動対応機能は未実装です）')) {
    console.log('Resolve queue item:', item)
    // Phase 2で実装予定
  }
}
</script>

<style scoped>
/* Component styles */
</style>

