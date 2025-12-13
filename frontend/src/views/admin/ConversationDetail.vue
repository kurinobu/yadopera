<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <div>
        <button
          @click="goBack"
          class="mb-4 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
        >
          ← ダッシュボードに戻る
        </button>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          会話詳細
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          セッションID: {{ sessionId }}
        </p>
      </div>
    </div>

    <!-- ローディング表示 -->
    <Loading v-if="loading" />

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchHistory"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- 会話情報 -->
    <template v-else-if="history">
      <!-- 会話情報カード -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          会話情報
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">セッションID</p>
            <p class="text-sm font-mono text-gray-900 dark:text-white">{{ history.session_id }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">言語</p>
            <p class="text-sm text-gray-900 dark:text-white">{{ history.language }}</p>
          </div>
          <div v-if="history.location">
            <p class="text-sm text-gray-500 dark:text-gray-400">設置場所</p>
            <p class="text-sm text-gray-900 dark:text-white">{{ getLocationName(history.location) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">開始時刻</p>
            <p class="text-sm text-gray-900 dark:text-white">{{ formatDateTime(history.started_at) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">最終活動時刻</p>
            <p class="text-sm text-gray-900 dark:text-white">{{ formatDateTime(history.last_activity_at) }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">メッセージ数</p>
            <p class="text-sm text-gray-900 dark:text-white">{{ history.messages.length }}</p>
          </div>
        </div>
      </div>

      <!-- メッセージ一覧 -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          メッセージ一覧
        </h2>
        <div class="space-y-4">
          <div
            v-for="message in history.messages"
            :key="message.id"
            class="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-b-0"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex items-center gap-2">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded',
                    message.role === 'user'
                      ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
                      : message.role === 'assistant'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                  ]"
                >
                  {{ getRoleName(message.role) }}
                </span>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatDateTime(message.created_at) }}
                </span>
              </div>
              <div v-if="message.ai_confidence !== null && message.ai_confidence !== undefined" class="text-xs text-gray-500 dark:text-gray-400">
                信頼度: {{ formatPercentage(Number(message.ai_confidence)) }}
              </div>
            </div>
            <p class="text-gray-900 dark:text-white whitespace-pre-wrap">{{ message.content }}</p>
            
            <!-- FAQカテゴリ表示 -->
            <div v-if="message.matched_faq_ids && message.matched_faq_ids.length > 0" class="mt-2">
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">使用したFAQ:</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="faqId in message.matched_faq_ids"
                  :key="faqId"
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded',
                    getCategoryColorClass(getFaqCategory(faqId))
                  ]"
                >
                  {{ getCategoryName(getFaqCategory(faqId)) }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Loading from '@/components/common/Loading.vue'
import { chatApi } from '@/api/chat'
import { faqApi } from '@/api/faq'
import { formatPercentage } from '@/utils/formatters'
import type { ChatHistoryResponse } from '@/types/chat'
import type { FAQ, FAQCategory } from '@/types/faq'

const route = useRoute()
const router = useRouter()

// パラメータからsession_idを取得
const sessionId = route.params.session_id as string

// データ状態
const loading = ref(true)
const error = ref<string | null>(null)
const history = ref<ChatHistoryResponse | null>(null)
const faqs = ref<FAQ[]>([])

// 会話履歴取得
const fetchHistory = async () => {
  try {
    loading.value = true
    error.value = null
    
    const data = await chatApi.getHistory(sessionId)
    history.value = data
  } catch (err: any) {
    console.error('Failed to fetch conversation history:', err)
    error.value = err.response?.data?.detail || '会話履歴の取得に失敗しました'
  } finally {
    loading.value = false
  }
}

// FAQ一覧取得
const fetchFaqs = async () => {
  try {
    const data = await faqApi.getFaqs()
    faqs.value = data
  } catch (err: any) {
    console.error('Failed to fetch FAQs:', err)
  }
}

// FAQカテゴリ取得
const getFaqCategory = (faqId: number): FAQCategory | null => {
  const faq = faqs.value.find(f => f.id === faqId)
  return faq ? faq.category : null
}

// ロール名取得
const getRoleName = (role: string): string => {
  switch (role) {
    case 'user':
      return 'ゲスト'
    case 'assistant':
      return 'AI'
    case 'system':
      return 'システム'
    default:
      return role
  }
}

// 設置場所名取得
const getLocationName = (location: string): string => {
  const locationMap: Record<string, string> = {
    entrance: '入口',
    room: '客室',
    kitchen: 'キッチン',
    lounge: 'ラウンジ'
  }
  return locationMap[location] || location
}

// カテゴリ名取得
const getCategoryName = (category: FAQCategory | null): string => {
  if (!category) return '不明'
  const categoryMap: Record<FAQCategory, string> = {
    basic: '基本情報',
    facilities: '設備・サービス',
    location: '場所・アクセス',
    trouble: 'トラブル対応'
  }
  return categoryMap[category] || category
}

// カテゴリ色クラス取得
const getCategoryColorClass = (category: FAQCategory | null): string => {
  if (!category) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  const colorMap: Record<FAQCategory, string> = {
    basic: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    facilities: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    location: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    trouble: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  return colorMap[category] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

// 日時フォーマット
const formatDateTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(d)
}

// 戻るボタン
const goBack = () => {
  router.push({ name: 'AdminDashboard' })
}

// コンポーネントマウント時
onMounted(async () => {
  await Promise.all([fetchHistory(), fetchFaqs()])
})
</script>


