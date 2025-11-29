/**
 * チャット状態管理（セッション管理含む）
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ChatMessage, Conversation } from '@/types/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSessionId = ref<string | null>(null)
  const sessionToken = ref<string | null>(null)
  const messages = ref<ChatMessage[]>([])
  const conversation = ref<Conversation | null>(null)
  const isLoading = ref(false)

  // Getters
  const hasMessages = computed(() => messages.value.length > 0)
  const hasSession = computed(() => !!currentSessionId.value)

  // Actions
  function setSessionId(sessionId: string | null) {
    currentSessionId.value = sessionId
    if (sessionId) {
      // Cookieに保存（useSession composableで実装）
    }
  }

  function setSessionToken(token: string | null) {
    sessionToken.value = token
  }

  function setMessages(newMessages: ChatMessage[]) {
    messages.value = newMessages
  }

  function addMessage(message: ChatMessage) {
    messages.value.push(message)
  }

  function setConversation(newConversation: Conversation | null) {
    conversation.value = newConversation
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function clearChat() {
    messages.value = []
    conversation.value = null
    currentSessionId.value = null
    sessionToken.value = null
  }

  return {
    currentSessionId,
    sessionToken,
    messages,
    conversation,
    isLoading,
    hasMessages,
    hasSession,
    setSessionId,
    setSessionToken,
    setMessages,
    addMessage,
    setConversation,
    setLoading,
    clearChat
  }
})

