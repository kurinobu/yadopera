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
    console.log('[chatStore] setMessages: 呼び出し', {
      oldMessagesCount: messages.value.length,
      oldMessages: messages.value,
      newMessagesCount: newMessages.length,
      newMessages: newMessages
    })
    messages.value = newMessages
    console.log('[chatStore] setMessages: 完了', {
      messagesCount: messages.value.length,
      messages: messages.value
    })
  }

  function addMessage(message: ChatMessage) {
    console.log('[chatStore] addMessage: 呼び出し', {
      message,
      messagesCountBefore: messages.value.length,
      messagesBefore: messages.value
    })
    messages.value.push(message)
    console.log('[chatStore] addMessage: 完了', {
      messagesCountAfter: messages.value.length,
      messagesAfter: messages.value
    })
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

