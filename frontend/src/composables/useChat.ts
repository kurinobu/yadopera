/**
 * チャットComposable
 */

import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { chatApi } from '@/api/chat'
import type { ChatRequest } from '@/types/chat'

export function useChat() {
  const chatStore = useChatStore()

  const messages = computed(() => chatStore.messages)
  const sessionId = computed(() => chatStore.currentSessionId)
  const isLoading = computed(() => chatStore.isLoading)

  async function sendMessage(request: ChatRequest) {
    console.log('[useChat] sendMessage: 開始', {
      request,
      messagesCountBefore: chatStore.messages.length,
      messagesBefore: chatStore.messages
    })
    
    try {
      chatStore.setLoading(true)
      const response = await chatApi.sendMessage(request)
      console.log('[useChat] sendMessage: APIレスポンス受信', {
        response,
        hasMessage: !!response.message,
        message: response.message
      })
      
      // メッセージを追加
      if (response.message) {
        console.log('[useChat] sendMessage: メッセージ追加前', {
          messagesCount: chatStore.messages.length,
          messages: chatStore.messages
        })
        chatStore.addMessage(response.message)
        console.log('[useChat] sendMessage: メッセージ追加後', {
          messagesCount: chatStore.messages.length,
          messages: chatStore.messages
        })
      } else {
        console.warn('[useChat] sendMessage: レスポンスにメッセージなし', { response })
      }

      // セッションIDを更新
      if (response.session_id) {
        console.log('[useChat] sendMessage: セッションID更新', {
          oldSessionId: chatStore.currentSessionId,
          newSessionId: response.session_id
        })
        chatStore.setSessionId(response.session_id)
      }

      console.log('[useChat] sendMessage: 完了', {
        messagesCount: chatStore.messages.length,
        messages: chatStore.messages
      })
      return response
    } catch (error) {
      console.error('[useChat] sendMessage: エラー', error, {
        messagesCount: chatStore.messages.length,
        messages: chatStore.messages
      })
      throw error
    } finally {
      chatStore.setLoading(false)
    }
  }

  async function loadHistory(sessionId: string, facilityId?: number) {
    console.log('[useChat] loadHistory: 開始', {
      sessionId,
      facilityId,
      messagesCountBefore: chatStore.messages.length,
      messagesBefore: chatStore.messages
    })
    
    try {
      chatStore.setLoading(true)
      const history = await chatApi.getHistory(sessionId, facilityId)
      console.log('[useChat] loadHistory: APIレスポンス受信', {
        history,
        hasMessages: !!history.messages,
        messagesCount: history.messages?.length || 0
      })
      
      if (history.messages) {
        console.log('[useChat] loadHistory: メッセージ設定前', {
          messagesCount: chatStore.messages.length,
          messages: chatStore.messages
        })
        chatStore.setMessages(history.messages)
        console.log('[useChat] loadHistory: メッセージ設定後', {
          messagesCount: chatStore.messages.length,
          messages: chatStore.messages
        })
      } else {
        console.warn('[useChat] loadHistory: 履歴にメッセージなし', { history })
      }

      return history
    } catch (error: any) {
      // 404エラー（会話が存在しない）の場合は無視して続行
      // これは新しいセッションの場合に正常な動作
      if (error?.response?.status === 404) {
        console.log('[useChat] loadHistory: 会話なし（404）- 正常', {
          messagesCount: chatStore.messages.length,
          messages: chatStore.messages
        })
        return null
      }
      // その他のエラーは再スロー
      console.error('[useChat] loadHistory: エラー', error, {
        messagesCount: chatStore.messages.length,
        messages: chatStore.messages
      })
      throw error
    } finally {
      chatStore.setLoading(false)
    }
  }

  function clearChat() {
    chatStore.clearChat()
  }

  return {
    messages,
    sessionId,
    isLoading,
    sendMessage,
    loadHistory,
    clearChat
  }
}

