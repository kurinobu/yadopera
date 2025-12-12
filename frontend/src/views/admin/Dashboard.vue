<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        ダッシュボード
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        週次サマリーとリアルタイムチャット履歴
      </p>
    </div>

    <!-- ローディング表示 -->
    <Loading v-if="loading" />

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchDashboardData"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- ダッシュボードコンテンツ -->
    <template v-else-if="dashboardData">
      <!-- 週次サマリー統計カード -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="総質問数"
          :value="summary.total_questions"
          subtitle="過去7日間"
          :icon="statsIcon"
          color="blue"
        />
        <StatsCard
          title="自動応答率"
          :value="formatPercentage(Number(summary.auto_response_rate))"
          subtitle="AIが回答した割合"
          :icon="responseIcon"
          color="green"
        />
        <StatsCard
          title="平均信頼度"
          :value="formatPercentage(Number(summary.average_confidence))"
          subtitle="AI回答の信頼度"
          :icon="confidenceIcon"
          color="purple"
        />
        <StatsCard
          title="未解決質問"
          :value="summary.unresolved_count"
          subtitle="エスカレーション待ち"
          :icon="unresolvedIcon"
          color="red"
        />
      </div>

      <!-- カテゴリ別円グラフ -->
      <CategoryChart :data="summary.category_breakdown" />

      <!-- リアルタイムチャット履歴と夜間対応キュー -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChatHistoryList
          :conversations="conversations"
          @click="handleConversationClick"
        />
        <OvernightQueueList
          :queue="overnightQueue"
          @view-all="() => {}"
        />
      </div>

      <!-- ゲストフィードバック集計 -->
      <FeedbackStats
        :stats="feedbackStats"
        @respond="handleFeedbackRespond"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, h } from 'vue'
import { useRouter } from 'vue-router'
import StatsCard from '@/components/admin/StatsCard.vue'
import CategoryChart from '@/components/admin/CategoryChart.vue'
import ChatHistoryList from '@/components/admin/ChatHistoryList.vue'
import OvernightQueueList from '@/components/admin/OvernightQueueList.vue'
import FeedbackStats from '@/components/admin/FeedbackStats.vue'
import Loading from '@/components/common/Loading.vue'
import { formatPercentage } from '@/utils/formatters'
import { dashboardApi } from '@/api/dashboard'
import type { DashboardData, ChatHistory, OvernightQueue, FeedbackStats as FeedbackStatsType, WeeklySummary } from '@/types/dashboard'

const router = useRouter()

// データ状態
const loading = ref(true)
const error = ref<string | null>(null)
const dashboardData = ref<DashboardData | null>(null)

// データ取得
const fetchDashboardData = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await dashboardApi.getDashboard()
    dashboardData.value = data
  } catch (err: any) {
    console.error('Failed to fetch dashboard data:', err)
    error.value = err.response?.data?.detail || 'ダッシュボードデータの取得に失敗しました'
  } finally {
    loading.value = false
  }
}

// コンポーネントマウント時にデータ取得
onMounted(() => {
  fetchDashboardData()
})

// 計算プロパティ（実データから取得）
const summary = computed(() => dashboardData.value?.summary || {
  period: { start: '', end: '' },
  total_questions: 0,
  auto_response_rate: 0,
  average_response_time_ms: 0,
  average_confidence: 0,
  category_breakdown: { basic: 0, facilities: 0, location: 0, trouble: 0 },
  top_questions: [],
  unresolved_count: 0
})

const conversations = computed(() => dashboardData.value?.recent_conversations || [])
const overnightQueue = computed(() => dashboardData.value?.overnight_queue || [])
const feedbackStats = computed(() => dashboardData.value?.feedback_stats || {
  positive_count: 0,
  negative_count: 0,
  positive_rate: 0,
  low_rated_answers: []
})

// アイコン定義
const statsIcon = () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' })
])

const responseIcon = () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' })
])

const confidenceIcon = () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M13 10V3L4 14h7v7l9-11h-7z' })
])

const unresolvedIcon = () => h('svg', { class: 'w-6 h-6', fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z' })
])

// イベントハンドラー
const handleConversationClick = (conversation: ChatHistory) => {
  router.push({
    name: 'ConversationDetail',
    params: { session_id: conversation.session_id }
  })
}

const handleQueueViewAll = () => {
  // 夜間対応キュー専用ページへの遷移はOvernightQueueListコンポーネント内で処理
  // この関数は必要に応じて追加の処理を行う（現時点では不要）
}

const handleFeedbackRespond = (answer: FeedbackStatsType['low_rated_answers'][0]) => {
  // FAQ管理ページにジャンプ（FeedbackStatsコンポーネント内で既に処理されている）
  // 必要に応じて、追加の処理をここに記述
  console.log('Navigate to FAQ management page for:', answer)
}
</script>

<style scoped>
/* Component styles */
</style>

