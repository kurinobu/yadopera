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
          <DarkModeToggle />
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
      v-if="facilityId !== null"
      :is-open="showTokenInput"
      :facility-id="facilityId"
      @update:is-open="showTokenInput = $event"
      @link="handleTokenLink"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChat } from '@/composables/useChat'
import { useSession } from '@/composables/useSession'
import { useFacilityStore } from '@/stores/facility'
import { useChatStore } from '@/stores/chat'
import { facilityApi } from '@/api/facility'
import { sessionApi } from '@/api/session'
import { chatApi } from '@/api/chat'
import ChatMessageList from '@/components/guest/ChatMessageList.vue'
import MessageInput from '@/components/guest/MessageInput.vue'
import EscalationButton from '@/components/guest/EscalationButton.vue'
import SessionTokenDisplay from '@/components/guest/SessionTokenDisplay.vue'
import SessionTokenInput from '@/components/guest/SessionTokenInput.vue'
import DarkModeToggle from '@/components/common/DarkModeToggle.vue'
import type { ChatMessage } from '@/types/chat'

const route = useRoute()
const router = useRouter()
const facilityStore = useFacilityStore()
const chatStore = useChatStore()
const { messages, isLoading, sendMessage, loadHistory } = useChat()
const { getOrCreateSessionId, linkSession, verifyToken } = useSession()

// 施設IDを取得（facilityStoreから取得、またはroute.paramsから取得）
const facilityId = computed(() => {
  // まず、facilityStoreから取得を試みる
  if (facilityStore.currentFacility?.id) {
    return facilityStore.currentFacility.id
  }
  
  // facilityStoreにない場合、route.paramsから取得を試みる
  // ただし、route.params.facilityIdはslug（文字列）の可能性がある
  const paramId = route.params.facilityId as string
  const parsedId = parseInt(paramId, 10)
  
  // 数値として有効な場合のみ返す
  if (!isNaN(parsedId)) {
    return parsedId
  }
  
  // それでも取得できない場合、エラーをログに記録
  console.error('[Chat.vue] facilityId取得失敗', {
    routeParams: route.params,
    currentFacility: facilityStore.currentFacility
  })
  
  return null
})

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
  console.log('[Chat.vue] onMounted: 開始', {
    initialMessage: initialMessage.value,
    initialQuestion: initialQuestion.value,
    messagesCount: messages.value.length,
    messages: messages.value,
    currentFacility: facilityStore.currentFacility,
    facilityId: facilityId.value
  })
  
  try {
    // 施設情報が取得されていない場合、取得する
    if (!facilityStore.currentFacility) {
      const slug = route.params.facilityId as string
      console.log('[Chat.vue] onMounted: 施設情報取得開始', { slug })
      try {
        const response = await facilityApi.getFacility(slug, location.value)
        facilityStore.setFacility(response.facility)
        facilityStore.setTopQuestions(response.top_questions)
        console.log('[Chat.vue] onMounted: 施設情報取得完了', {
          facility: response.facility,
          facilityId: response.facility.id
        })
      } catch (err) {
        console.error('[Chat.vue] onMounted: 施設情報取得エラー', err)
        error.value = '施設情報の取得に失敗しました'
        return
      }
    } else {
      console.log('[Chat.vue] onMounted: 施設情報は既に取得済み', {
        facility: facilityStore.currentFacility,
        facilityId: facilityStore.currentFacility.id
      })
    }
    
    // 施設IDが取得できない場合、エラーを返す
    if (!facilityId.value) {
      console.error('[Chat.vue] onMounted: facilityId取得失敗', {
        routeParams: route.params,
        currentFacility: facilityStore.currentFacility
      })
      error.value = '施設IDの取得に失敗しました'
      return
    }
    
    // セッションIDを取得または生成
    const currentSessionId = getOrCreateSessionId()
    console.log('[Chat.vue] onMounted: セッションID取得', { currentSessionId })

    // セッション統合トークンを生成・取得
    if (currentSessionId && facilityId.value) {
      try {
        console.log('[Chat.vue] onMounted: トークン取得開始', {
          sessionId: currentSessionId,
          facilityId: facilityId.value
        })
        
        // 既存のトークンを取得を試みる
        try {
          const existingToken = await sessionApi.getTokenBySessionId(currentSessionId)
          console.log('[Chat.vue] onMounted: 既存トークン取得成功', {
            token: existingToken.token,
            expiresAt: existingToken.expires_at
          })
          chatStore.setSessionToken(existingToken.token)
          tokenExpiresAt.value = existingToken.expires_at
          await nextTick() // Vueのレンダリングサイクルを明示的にトリガー
        } catch (err: any) {
          // 404エラー（トークンが存在しない）の場合は新規生成
          if (err?.code === 'NOT_FOUND') {
            console.log('[Chat.vue] onMounted: 既存トークンなし - 新規生成', {
              sessionId: currentSessionId,
              facilityId: facilityId.value
            })
            const newToken = await sessionApi.generateToken({
              facility_id: facilityId.value,
              session_id: currentSessionId
            })
            console.log('[Chat.vue] onMounted: トークン生成成功', {
              token: newToken.token,
              expiresAt: newToken.expires_at
            })
            chatStore.setSessionToken(newToken.token)
            tokenExpiresAt.value = newToken.expires_at
            await nextTick() // Vueのレンダリングサイクルを明示的にトリガー
          } else {
            // その他のエラーはログに記録するが、チャット機能は継続できる
            console.error('[Chat.vue] onMounted: トークン取得エラー', err)
          }
        }
      } catch (err) {
        // トークン生成・取得に失敗してもチャット機能は継続できる
        console.error('[Chat.vue] onMounted: トークン生成・取得エラー', err)
      }
    }

    // 初期メッセージまたは質問がある場合は、会話履歴取得をスキップ
    // （まだ会話が存在しないため、404エラーが発生する）
    const hasInitialMessage = initialMessage.value || initialQuestion.value
    console.log('[Chat.vue] onMounted: 初期メッセージチェック', { hasInitialMessage })

    // 既存の会話履歴を読み込む（初期メッセージがない場合のみ）
    if (currentSessionId && !hasInitialMessage) {
      try {
        console.log('[Chat.vue] onMounted: 会話履歴読み込み開始', {
          sessionId: currentSessionId,
          facilityId: facilityId.value
        })
        await loadHistory(currentSessionId, facilityId.value)
        console.log('[Chat.vue] onMounted: 会話履歴読み込み完了', {
          messagesCount: messages.value.length,
          messages: messages.value
        })
      } catch (err: any) {
        // 404エラー（会話が存在しない）の場合は無視して続行
        // これは新しいセッションの場合に正常な動作
        if (err?.code !== 'NOT_FOUND') {
          console.error('[Chat.vue] onMounted: 会話履歴読み込みエラー', err)
        } else {
          console.log('[Chat.vue] onMounted: 会話履歴なし（404）- 正常', {
            messagesCount: messages.value.length,
            messages: messages.value
          })
        }
      }
    }

    // 初期メッセージまたは質問を送信
    if (initialMessage.value) {
      console.log('[Chat.vue] onMounted: 初期メッセージ送信開始', {
        message: initialMessage.value,
        messagesCountBefore: messages.value.length,
        facilityId: facilityId.value
      })
      await handleMessageSubmit(initialMessage.value)
      console.log('[Chat.vue] onMounted: 初期メッセージ送信完了', {
        messagesCountAfter: messages.value.length,
        messages: messages.value
      })
    } else if (initialQuestion.value) {
      console.log('[Chat.vue] onMounted: 初期質問送信開始', {
        question: initialQuestion.value,
        messagesCountBefore: messages.value.length,
        facilityId: facilityId.value
      })
      await handleMessageSubmit(initialQuestion.value)
      console.log('[Chat.vue] onMounted: 初期質問送信完了', {
        messagesCountAfter: messages.value.length,
        messages: messages.value
      })
    }
    
    console.log('[Chat.vue] onMounted: 完了', {
      messagesCount: messages.value.length,
      messages: messages.value,
      facilityId: facilityId.value
    })
  } catch (err) {
    console.error('[Chat.vue] onMounted: エラー', err)
    error.value = 'チャットの初期化に失敗しました'
  }
})

// メッセージ送信
const handleMessageSubmit = async (message: string) => {
  console.log('[Chat.vue] handleMessageSubmit: 開始', {
    message,
    facilityId: facilityId.value,
    messagesCountBefore: messages.value.length,
    messagesBefore: messages.value
  })
  
  if (!facilityId.value || !message.trim()) {
    console.warn('[Chat.vue] handleMessageSubmit: バリデーションエラー', {
      facilityId: facilityId.value,
      message: message.trim()
    })
    return
  }

  try {
    error.value = null

    // セッションIDを取得または生成
    const currentSessionId = getOrCreateSessionId()
    console.log('[Chat.vue] handleMessageSubmit: セッションID', { currentSessionId })

    // ユーザーメッセージを即座に表示（楽観的更新）
    const userMessage: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: message.trim(),
      created_at: new Date().toISOString()
    }
    console.log('[Chat.vue] handleMessageSubmit: ユーザーメッセージ追加前', {
      messagesCount: messages.value.length,
      messages: messages.value
    })
    chatStore.addMessage(userMessage)
    console.log('[Chat.vue] handleMessageSubmit: ユーザーメッセージ追加後', {
      messagesCount: messages.value.length,
      messages: messages.value
    })

    // AI応答を取得
    console.log('[Chat.vue] handleMessageSubmit: AI応答取得開始')
    const response = await sendMessage({
      facility_id: facilityId.value,
      message: message.trim(),
      language: language.value,
      location: location.value,
      session_id: currentSessionId || undefined
    })
    console.log('[Chat.vue] handleMessageSubmit: AI応答取得完了', {
      response,
      messagesCountAfter: messages.value.length,
      messagesAfter: messages.value
    })

    // エスカレーションが必要な場合
    if (response.is_escalated) {
      // TODO: エスカレーション処理（Week 4で実装）
      console.log('[Chat.vue] handleMessageSubmit: エスカレーション必要', response.escalation_id)
    }
  } catch (err: any) {
    console.error('[Chat.vue] handleMessageSubmit: エラー', err, {
      messagesCount: messages.value.length,
      messages: messages.value
    })
    error.value = err.message || 'メッセージの送信に失敗しました'
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
const handleEscalation = async () => {
  try {
    const currentSessionId = getOrCreateSessionId()
    
    if (!facilityId.value) {
      console.error('[Chat.vue] handleEscalation: facilityId取得失敗')
      alert('施設IDの取得に失敗しました。ページをリロードしてください。')
      return
    }
    
    if (!currentSessionId) {
      console.error('[Chat.vue] handleEscalation: sessionId取得失敗')
      alert('セッションIDの取得に失敗しました。ページをリロードしてください。')
      return
    }
    
    console.log('[Chat.vue] handleEscalation: エスカレーション開始', {
      facilityId: facilityId.value,
      sessionId: currentSessionId
    })
    
    // エスカレーションAPIを呼び出し
    const response = await chatApi.escalateToStaff({
      facility_id: facilityId.value,
      session_id: currentSessionId
    })
    
    console.log('[Chat.vue] handleEscalation: エスカレーション成功', response)
    
    // 成功メッセージを表示（多言語対応）
    const message = language.value === 'ja' 
      ? 'スタッフに連絡しました。スタッフが対応いたします。'
      : 'We have contacted the staff. They will respond to you shortly.'
    
    alert(message)
    
    // エスカレーション成功をメッセージとして表示（オプション）
    // メッセージリストにシステムメッセージを追加することも可能
    
  } catch (err: any) {
    console.error('[Chat.vue] handleEscalation: エラー', err)
    
    // エラーメッセージをユーザーフレンドリーに変換
    let errorMessage = language.value === 'ja'
      ? 'エスカレーションの作成に失敗しました。'
      : 'Failed to contact staff.'
    
    const detail = err.response?.data?.detail || err.message || ''
    
    if (detail.includes('Conversation not found')) {
      errorMessage = language.value === 'ja'
        ? '会話が見つかりませんでした。メッセージを送信してから再度お試しください。'
        : 'Conversation not found. Please send a message first and try again.'
    } else if (detail) {
      errorMessage = language.value === 'ja'
        ? `エスカレーションの作成に失敗しました: ${detail}`
        : `Failed to contact staff: ${detail}`
    }
    
    alert(errorMessage)
  }
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
    if (facilityId.value !== null) {
      await linkSession(facilityId.value, token)

      // 会話履歴を再読み込み
      const currentSessionId = getOrCreateSessionId()
      if (currentSessionId) {
        await loadHistory(currentSessionId, facilityId.value)
      }
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

