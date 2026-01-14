<template>
  <div class="flex flex-col h-full">
    <!-- Chat Messages Area -->
    <div ref="messagesContainer" class="flex-1 overflow-y-auto p-6 space-y-4">
      <!-- Welcome Message -->
      <div v-if="!helpStore.hasChatMessages" class="text-center py-12">
        <div class="inline-block p-4 bg-indigo-100 dark:bg-indigo-900 rounded-full mb-4">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-12 w-12 text-indigo-600 dark:text-indigo-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
            />
          </svg>
        </div>
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          AIヘルプアシスタント
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 max-w-md mx-auto">
          何でも質問してください。システムの使い方や設定方法について、AIがお答えします。
        </p>
      </div>

      <!-- Chat Messages -->
      <ChatMessage
        v-for="message in helpStore.chatMessages"
        :key="message.id"
        :message="message"
      />

      <!-- Loading Indicator -->
      <div v-if="helpStore.isChatting" class="flex items-start space-x-3">
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5 text-indigo-600 dark:text-indigo-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
        </div>
        <div class="flex-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-4">
          <div class="flex space-x-2">
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce"></div>
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
            <div class="w-2 h-2 bg-gray-400 dark:bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="border-t border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800">
      <!-- Clear History Button -->
      <div v-if="helpStore.hasChatMessages" class="mb-3 text-center">
        <button
          @click="handleClearHistory"
          class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 hover:underline"
        >
          履歴をクリア
        </button>
      </div>

      <!-- Input Form -->
      <form @submit.prevent="handleSendMessage" class="flex items-end space-x-3">
        <div class="flex-1">
          <textarea
            v-model="messageInput"
            placeholder="質問を入力してください..."
            rows="2"
            class="
              w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600
              bg-white dark:bg-gray-700 text-gray-900 dark:text-white
              focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
              resize-none transition-all
            "
            :disabled="helpStore.isChatting"
            @keydown.enter.exact.prevent="handleSendMessage"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Enterで送信、Shift+Enterで改行
          </p>
        </div>
        <button
          type="submit"
          :disabled="!messageInput.trim() || helpStore.isChatting"
          class="
            px-6 py-3 rounded-lg font-medium
            bg-indigo-600 text-white
            hover:bg-indigo-700
            disabled:bg-gray-300 disabled:cursor-not-allowed dark:disabled:bg-gray-600
            transition-colors
          "
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch } from 'vue'
import { useHelpStore } from '@/stores/help'
import ChatMessage from './ChatMessage.vue'

const helpStore = useHelpStore()

// State
const messageInput = ref('')
const messagesContainer = ref<HTMLElement | null>(null)

// Methods
const handleSendMessage = async () => {
  if (!messageInput.value.trim() || helpStore.isChatting) {
    return
  }

  const message = messageInput.value
  messageInput.value = ''

  await helpStore.sendChatMessage(message)
  await scrollToBottom()
}

const handleClearHistory = () => {
  if (confirm('チャット履歴を削除しますか？')) {
    helpStore.clearChat()
  }
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// Watch messages changes and scroll
watch(
  () => helpStore.chatMessages.length,
  () => {
    scrollToBottom()
  }
)
</script>

