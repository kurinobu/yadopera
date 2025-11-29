<template>
  <div class="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
    <!-- ヘッダー（固定） -->
    <div class="flex-shrink-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-4 py-3">
      <div class="flex items-center justify-between mb-2">
        <div class="flex items-center space-x-3">
          <button
            @click="handleBack"
            class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            aria-label="戻る"
          >
            <svg class="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h1 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ facility?.name || 'Chat' }}
          </h1>
        </div>
        <div class="flex items-center space-x-2">
          <button
            @click="showTokenInput = true"
            class="px-3 py-1.5 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          >
            トークン統合 / Link
          </button>
          <EscalationButton
            :disabled="isLoading"
            @escalation="handleEscalation"
          />
        </div>
      </div>
      <!-- セッション統合トークン表示 -->
      <SessionTokenDisplay
        :token="sessionToken"
        :expires-at="tokenExpiresAt"
        @copy="handleTokenCopy"
      />
    </div>

    <!-- メッセージリスト（スクロール可能） -->
    <ChatMessageList
      :messages="messages"
      :show-feedback="true"
      @feedback="handleFeedback"
      class="flex-1 min-h-0"
    />

    <!-- ローディング表示 -->
    <div
      v-if="isLoading"
      class="flex-shrink-0 px-4 py-2 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700"
    >
      <div class="flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400">
        <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
        </svg>
        <span>AIが回答を生成中...</span>
      </div>
    </div>

    <!-- メッセージ入力（固定フッター） -->
    <div class="flex-shrink-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 px-4 py-3">
      <MessageInput
        :disabled="isLoading"
        placeholder="メッセージを入力..."
        @submit="handleMessageSubmit"
      />
    </div>

    <!-- エラー表示 -->
    <div
      v-if="error"
      class="fixed bottom-20 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 shadow-lg"
    >
      <div class="flex items-start space-x-3">
        <svg class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-red-900 dark:text-red-300">
            エラーが発生しました
          </p>
          <p class="text-sm text-red-800 dark:text-red-400 mt-1">
            {{ error }}
          </p>
        </div>
        <button
          @click="error = null"
          class="text-red-400 hover:text-red-600 dark:hover:text-red-300"
          aria-label="閉じる"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- セッション統合トークン入力モーダル -->
    <SessionTokenInput
      :is-open="showTokenInput"
      :facility-id="facilityId"
      @update:is-open="showTokenInput = $event"
      @link="handleTokenLink"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChat } from '@/composables/useChat'
import { useSession } from '@/composables/useSession'
import { useFacilityStore } from '@/stores/facility'
import { useChatStore } from '@/stores/chat'
import ChatMessageList from '@/components/guest/ChatMessageList.vue'
import MessageInput from '@/components/guest/MessageInput.vue'
import EscalationButton from '@/components/guest/EscalationButton.vue'
import SessionTokenDisplay from '@/components/guest/SessionTokenDisplay.vue'
import SessionTokenInput from '@/components/guest/SessionTokenInput.vue'
import type { ChatMessage } from '@/types/chat'

const route = useRoute()
const router = useRouter()
const facilityStore = useFacilityStore()
const chatStore = useChatStore()
const { messages, sessionId, isLoading, sendMessage, loadHistory } = useChat()
const { getOrCreateSessionId, linkSession, verifyToken } = useSession()

const facilityId = computed(() => parseInt(route.params.facilityId as string, 10))
const language = computed(() => (route.query.lang as string) || 'en')
const location = computed(() => (route.query.location as string) || undefined)
const initialMessage = computed(() => route.query.message as string | undefined)
const initialQuestion = computed(() => route.query.question as string | undefined)

const facility = computed(() => facilityStore.currentFacility)
const error = ref<string | null>(null)
const sessionToken = computed(() => chatStore.sessionToken)
const tokenExpiresAt = ref<string | null>(null)
const showTokenInput = ref(false)

// 初期メッセージまたは質問を送信
onMounted(async () => {
  try {
    // セッションIDを取得または生成
    const currentSessionId = getOrCreateSessionId()

    // 既存の会話履歴を読み込む
    if (currentSessionId) {
      await loadHistory(currentSessionId, facilityId.value)
    }

    // 初期メッセージまたは質問を送信
    if (initialMessage.value) {
      await handleMessageSubmit(initialMessage.value)
    } else if (initialQuestion.value) {
      await handleMessageSubmit(initialQuestion.value)
    }
  } catch (err) {
    console.error('Chat initialization error:', err)
  }
})

// メッセージ送信
const handleMessageSubmit = async (message: string) => {
  if (!facilityId.value || !message.trim()) {
    return
  }

  try {
    error.value = null

    // セッションIDを取得または生成
    const currentSessionId = getOrCreateSessionId()

    // ユーザーメッセージを即座に表示（楽観的更新）
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: message.trim(),
      created_at: new Date().toISOString()
    }
    chatStore.addMessage(userMessage)

    // AI応答を取得
    const response = await sendMessage({
      facility_id: facilityId.value,
      message: message.trim(),
      language: language.value,
      location: location.value,
      session_id: currentSessionId || undefined
    })

    // エスカレーションが必要な場合
    if (response.is_escalated) {
      // TODO: エスカレーション処理（Week 4で実装）
      console.log('Escalation needed:', response.escalation_id)
    }
  } catch (err: any) {
    error.value = err.message || 'メッセージの送信に失敗しました'
    console.error('Message send error:', err)
  }
}

// フィードバック送信
const handleFeedback = async (messageId: number, type: 'positive' | 'negative') => {
  try {
    // TODO: Week 4でAPI連携を実装
    // 現在はモック処理
    console.log('Feedback:', messageId, type)
  } catch (err) {
    console.error('Feedback error:', err)
  }
}

// エスカレーション
const handleEscalation = () => {
  // TODO: Week 4でエスカレーション処理を実装
  console.log('Escalation requested')
}

// 戻る
const handleBack = () => {
  router.push({
    name: 'Welcome',
    params: { facilityId: route.params.facilityId },
    query: { lang: language.value, location: location.value }
  })
}

// セッション統合トークン統合
const handleTokenLink = async (token: string) => {
  try {
    error.value = null

    // トークンを検証
    const isValid = await verifyToken(token)
    if (!isValid) {
      error.value = '無効なトークンです / Invalid token'
      return
    }

    // セッション統合
    await linkSession(facilityId.value, token)

    // 会話履歴を再読み込み
    const currentSessionId = getOrCreateSessionId()
    if (currentSessionId) {
      await loadHistory(currentSessionId, facilityId.value)
    }

    // TODO: Week 4でトークン取得APIを実装
    // 現在はモック処理
    chatStore.setSessionToken(token)
    tokenExpiresAt.value = new Date(Date.now() + 10 * 60 * 1000).toISOString() // 10分後
  } catch (err: any) {
    error.value = err.message || 'セッション統合に失敗しました'
    console.error('Token link error:', err)
  }
}

// トークンコピー
const handleTokenCopy = (token: string) => {
  // TODO: トースト通知を表示（Week 4で実装）
  console.log('Token copied:', token)
}
</script>

<style scoped>
/* Component styles */
</style>

