<template>
  <div
    ref="messageListRef"
    class="flex-1 overflow-y-auto px-4 py-4 space-y-4"
    :class="containerClasses"
  >
    <!-- メッセージがない場合 -->
    <div
      v-if="messages.length === 0"
      class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400"
    >
      <p class="text-sm">メッセージがありません</p>
    </div>

    <!-- メッセージリスト -->
    <ChatMessageComponent
      v-for="message in messages"
      :key="message.id"
      :message="message"
      :show-feedback="showFeedback"
      @feedback="handleFeedback"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, onMounted } from 'vue'
import type { ChatMessage } from '@/types/chat'
import ChatMessageComponent from './ChatMessage.vue'

interface Props {
  messages: ChatMessage[]
  showFeedback?: boolean
  containerClasses?: string
}

const props = withDefaults(defineProps<Props>(), {
  showFeedback: true,
  containerClasses: ''
})

const emit = defineEmits<{
  feedback: [messageId: number, type: 'positive' | 'negative']
}>()

const messageListRef = ref<HTMLElement | null>(null)

// 最新メッセージに自動スクロール
const scrollToBottom = () => {
  nextTick(() => {
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight
    }
  })
}

// メッセージが追加されたら自動スクロール
watch(() => props.messages.length, (newLength, oldLength) => {
  console.log('[ChatMessageList] messages.length 変更', {
    oldLength,
    newLength,
    messages: props.messages
  })
  scrollToBottom()
})

// messagesプロップの変更を監視
watch(() => props.messages, (newMessages, oldMessages) => {
  console.log('[ChatMessageList] messages 変更', {
    oldMessagesCount: oldMessages?.length || 0,
    newMessagesCount: newMessages?.length || 0,
    oldMessages,
    newMessages
  })
}, { deep: true })

onMounted(() => {
  console.log('[ChatMessageList] onMounted', {
    messagesCount: props.messages.length,
    messages: props.messages
  })
  scrollToBottom()
})

const handleFeedback = (messageId: number, type: 'positive' | 'negative') => {
  emit('feedback', messageId, type)
}
</script>

<style scoped>
/* Component styles */
</style>

