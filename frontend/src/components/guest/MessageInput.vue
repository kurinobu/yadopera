<template>
  <div class="w-full">
    <label
      for="message-input"
      class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
    >
      メッセージを入力 / Enter your message
    </label>
    <div class="flex space-x-2">
      <input
        id="message-input"
        v-model="message"
        type="text"
        :placeholder="placeholder"
        :maxlength="maxLength"
        :disabled="disabled"
        class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
        @keyup.enter="handleSubmit"
      />
      <button
        @click="handleSubmit"
        :disabled="disabled || !canSubmit"
        class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        <svg
          class="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
    </div>
    <p v-if="showCharCount" class="mt-1 text-xs text-gray-500 dark:text-gray-400 text-right">
      {{ message.length }} / {{ maxLength }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { MIN_MESSAGE_LENGTH, MAX_MESSAGE_LENGTH } from '@/utils/constants'

interface Props {
  placeholder?: string
  disabled?: boolean
  showCharCount?: boolean
  maxLength?: number
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '質問を入力してください...',
  disabled: false,
  showCharCount: true,
  maxLength: MAX_MESSAGE_LENGTH
})

const emit = defineEmits<{
  submit: [message: string]
}>()

const message = ref('')

const canSubmit = computed(() => {
  return message.value.trim().length >= MIN_MESSAGE_LENGTH && message.value.length <= props.maxLength
})

const handleSubmit = () => {
  if (canSubmit.value && !props.disabled) {
    emit('submit', message.value.trim())
    message.value = ''
  }
}
</script>

<style scoped>
/* Component styles */
</style>


