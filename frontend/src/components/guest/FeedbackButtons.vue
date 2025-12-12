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
      <span class="text-2xl">👍</span>
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
      <span class="text-2xl">👎</span>
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

