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

    <!-- 週次サマリー統計カード -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <StatsCard
        title="総質問数"
        :value="mockSummary.total_questions"
        subtitle="過去7日間"
        :icon="statsIcon"
        color="blue"
      />
      <StatsCard
        title="自動応答率"
        :value="formatPercentage(mockSummary.auto_response_rate)"
        subtitle="AIが回答した割合"
        :icon="responseIcon"
        color="green"
      />
      <StatsCard
        title="平均信頼度"
        :value="formatPercentage(mockSummary.average_confidence)"
        subtitle="AI回答の信頼度"
        :icon="confidenceIcon"
        color="purple"
      />
      <StatsCard
        title="未解決質問"
        :value="mockSummary.unresolved_count"
        subtitle="エスカレーション待ち"
        :icon="unresolvedIcon"
        color="red"
      />
    </div>

    <!-- カテゴリ別円グラフ -->
    <CategoryChart :data="mockSummary.category_breakdown" />

    <!-- リアルタイムチャット履歴と夜間対応キュー -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <ChatHistoryList
        :conversations="mockConversations"
        @click="handleConversationClick"
      />
      <OvernightQueueList
        :queue="mockOvernightQueue"
        @resolve="handleQueueResolve"
      />
    </div>

    <!-- ゲストフィードバック集計 -->
    <FeedbackStats
      :stats="mockFeedbackStats"
      @improve="handleFeedbackImprove"
      @ignore="handleFeedbackIgnore"
    />
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import StatsCard from '@/components/admin/StatsCard.vue'
import CategoryChart from '@/components/admin/CategoryChart.vue'
import ChatHistoryList from '@/components/admin/ChatHistoryList.vue'
import OvernightQueueList from '@/components/admin/OvernightQueueList.vue'
import FeedbackStats from '@/components/admin/FeedbackStats.vue'
import { formatPercentage } from '@/utils/formatters'
import type { ChatHistory, OvernightQueue, FeedbackStats as FeedbackStatsType } from '@/types/dashboard'

// モックデータ（Week 4でAPI連携に置き換え）
const mockSummary = {
  period: {
    start: '2025-11-11T00:00:00Z',
    end: '2025-11-18T00:00:00Z'
  },
  total_questions: 127,
  auto_response_rate: 0.88,
  average_response_time_ms: 2150,
  average_confidence: 0.85,
  category_breakdown: {
    basic: 35,
    facilities: 48,
    location: 25,
    trouble: 7
  },
  top_questions: [
    { question: 'WiFi password?', count: 23 },
    { question: 'Check-in time?', count: 18 }
  ],
  unresolved_count: 8
}

const mockConversations: ChatHistory[] = [
  {
    session_id: '550e8400-e29b-41d4-a716-446655440000',
    guest_language: 'en',
    last_message: 'Where is the laundry room?',
    ai_confidence: 0.92,
    created_at: new Date(Date.now() - 5 * 60000).toISOString() // 5分前
  },
  {
    session_id: '550e8400-e29b-41d4-a716-446655440001',
    guest_language: 'ja',
    last_message: 'WiFiのパスワードを教えてください',
    ai_confidence: 0.95,
    created_at: new Date(Date.now() - 15 * 60000).toISOString() // 15分前
  },
  {
    session_id: '550e8400-e29b-41d4-a716-446655440002',
    guest_language: 'en',
    last_message: 'What time is check-out?',
    ai_confidence: 0.88,
    created_at: new Date(Date.now() - 30 * 60000).toISOString() // 30分前
  }
]

const mockOvernightQueue: OvernightQueue[] = [
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
  }
]

const mockFeedbackStats: FeedbackStatsType = {
  positive_count: 95,
  negative_count: 12,
  positive_rate: 0.89,
  low_rated_answers: [
    {
      message_id: 101,
      question: 'WiFi password?',
      answer: 'The password is guest2024.',
      negative_count: 3
    },
    {
      message_id: 102,
      question: 'Check-in time?',
      answer: 'Check-in is from 3pm to 10pm.',
      negative_count: 2
    }
  ]
}

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
  // TODO: Week 4で会話詳細画面への遷移を実装
  console.log('Conversation clicked:', conversation)
}

const handleQueueResolve = (item: OvernightQueue) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Queue item resolved:', item)
}

const handleFeedbackImprove = (answer: FeedbackStatsType['low_rated_answers'][0]) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Feedback improve:', answer)
}

const handleFeedbackIgnore = (answer: FeedbackStatsType['low_rated_answers'][0]) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Feedback ignore:', answer)
}
</script>

<style scoped>
/* Component styles */
</style>

