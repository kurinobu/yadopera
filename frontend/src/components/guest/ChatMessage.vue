<template>
  <div
    :class="[
      'flex mb-4',
      message.role === 'user' ? 'justify-end' : 'justify-start'
    ]"
  >
    <div
      :class="[
        'max-w-[80%] md:max-w-[70%] rounded-lg px-4 py-2',
        message.role === 'user'
          ? 'bg-blue-600 text-white'
          : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
      ]"
    >
      <!-- メッセージ内容 -->
      <p class="text-sm whitespace-pre-wrap break-words">
        {{ message.content }}
      </p>

      <!-- AI信頼度表示（assistantのみ、オプション） -->
      <div
        v-if="message.role === 'assistant' && message.ai_confidence !== undefined"
        class="mt-2 text-xs opacity-75"
      >
        信頼度: {{ formatConfidence(message.ai_confidence) }}
      </div>

      <!-- タイムスタンプ -->
      <p
        :class="[
          'text-xs mt-1',
          message.role === 'user'
            ? 'text-blue-100'
            : 'text-gray-500 dark:text-gray-400'
        ]"
      >
        {{ formatTime(message.created_at) }}
      </p>

      <!-- フィードバックボタン（assistantのみ） -->
      <FeedbackButtons
        v-if="message.role === 'assistant' && showFeedback"
        :message-id="message.id"
        @feedback="handleFeedback"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatTime, formatConfidence } from '@/utils/formatters'
import type { ChatMessage } from '@/types/chat'
import FeedbackButtons from './FeedbackButtons.vue'

interface Props {
  message: ChatMessage
  showFeedback?: boolean
}

withDefaults(defineProps<Props>(), {
  showFeedback: true
})

const emit = defineEmits<{
  feedback: [messageId: number, type: 'positive' | 'negative']
}>()

const handleFeedback = (messageId: number, type: 'positive' | 'negative') => {
  emit('feedback', messageId, type)
}
</script>

<style scoped>
/* Component styles */
</style>

