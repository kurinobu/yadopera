<template>
  <div class="flex items-center space-x-2 mt-2">
    <span class="text-xs text-gray-500 dark:text-gray-400 mr-2">
      役に立ちましたか？ / Was this helpful?
    </span>
    <button
      @click="handleFeedback('positive')"
      :disabled="feedbackSent"
      :class="[
        'p-1.5 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500',
        feedbackType === 'positive'
          ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600',
        feedbackSent && feedbackType !== 'positive' ? 'opacity-50 cursor-not-allowed' : ''
      ]"
      aria-label="役に立った"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.834a1 1 0 001.803.618l1.723-2.554a1 1 0 01.14-.494l.806-2.41a2 2 0 00-.092-1.664l-1.008-1.675A1 1 0 006 10.333zM16 7h-1a2 2 0 01-2-2V2.5a2 2 0 012-2h1a2 2 0 012 2V5a2 2 0 01-2 2zM11.362 5.214L8.616 3.5a1.5 1.5 0 00-2.232 1.39l.213 2.5a1 1 0 001.227.894l2.693-.48a1.5 1.5 0 10-.803-2.596z" />
      </svg>
    </button>
    <button
      @click="handleFeedback('negative')"
      :disabled="feedbackSent"
      :class="[
        'p-1.5 rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500',
        feedbackType === 'negative'
          ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600',
        feedbackSent && feedbackType !== 'negative' ? 'opacity-50 cursor-not-allowed' : ''
      ]"
      aria-label="役に立たなかった"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.834a1 1 0 00-1.803-.618l-1.723 2.554a1 1 0 01-.14.494l-.806 2.41a2 2 0 00.092 1.664l1.008 1.675A1 1 0 0014 9.667zM4 13h1a2 2 0 012 2v4.5a2 2 0 01-2 2H4a2 2 0 01-2-2V15a2 2 0 012-2zM8.638 14.786l2.746 1.714a1.5 1.5 0 002.232-1.39l-.213-2.5a1 1 0 00-1.227-.894l-2.693.48a1.5 1.5 0 10.803 2.596z" />
      </svg>
    </button>
    <span
      v-if="feedbackSent"
      class="text-xs text-green-600 dark:text-green-400 ml-2"
    >
      ありがとうございます / Thank you!
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { chatApi } from '@/api/chat'

interface Props {
  messageId: number
}

const props = defineProps<Props>()

const emit = defineEmits<{
  feedback: [messageId: number, type: 'positive' | 'negative']
}>()

const feedbackType = ref<'positive' | 'negative' | null>(null)
const feedbackSent = ref(false)

const handleFeedback = async (type: 'positive' | 'negative') => {
  if (feedbackSent.value) {
    return
  }

  feedbackType.value = type

  try {
    // API連携実装（Week 4）
    await chatApi.sendFeedback({
      message_id: props.messageId,
      feedback_type: type
    })
    
    feedbackSent.value = true
    emit('feedback', props.messageId, type)
  } catch (error) {
    console.error('Feedback error:', error)
    feedbackSent.value = false
    feedbackType.value = null
    // エラー通知（必要に応じて）
    alert('フィードバックの送信に失敗しました。もう一度お試しください。')
  }
}
</script>

<style scoped>
/* Component styles */
</style>

