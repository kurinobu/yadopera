/**
 * チャットComposable
 */

import { computed } from 'vue'
import { useChatStore } from '@/stores/chat'
import { chatApi } from '@/api/chat'
import type { ChatRequest, ChatResponse } from '@/types/chat'

export function useChat() {
  const chatStore = useChatStore()

  const messages = computed(() => chatStore.messages)
  const sessionId = computed(() => chatStore.currentSessionId)
  const isLoading = computed(() => chatStore.isLoading)

  async function sendMessage(request: ChatRequest) {
    try {
      chatStore.setLoading(true)
      const response = await chatApi.sendMessage(request)
      
      // メッセージを追加
      if (response.message) {
        chatStore.addMessage(response.message)
      }

      // セッションIDを更新
      if (response.session_id) {
        chatStore.setSessionId(response.session_id)
      }

      return response
    } catch (error) {
      throw error
    } finally {
      chatStore.setLoading(false)
    }
  }

  async function loadHistory(sessionId: string, facilityId?: number) {
    try {
      chatStore.setLoading(true)
      const history = await chatApi.getHistory(sessionId, facilityId)
      
      if (history.messages) {
        chatStore.setMessages(history.messages)
      }

      return history
    } catch (error) {
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

