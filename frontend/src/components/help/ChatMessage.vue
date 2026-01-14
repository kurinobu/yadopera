<template>
  <div
    :class="[
      'flex items-start space-x-3',
      message.role === 'user' ? 'justify-end' : 'justify-start',
    ]"
  >
    <!-- Assistant Avatar -->
    <div
      v-if="message.role === 'assistant'"
      class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center"
    >
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

    <!-- Message Content -->
    <div
      :class="[
        'max-w-[70%] rounded-lg p-4',
        message.role === 'user'
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white',
      ]"
    >
      <p class="text-sm whitespace-pre-wrap">{{ message.content }}</p>

      <!-- Related URL -->
      <div v-if="message.related_url && message.role === 'assistant'" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
        <a
          :href="message.related_url"
          class="inline-flex items-center text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline"
          target="_blank"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            class="h-4 w-4 mr-1"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 7l5 5m0 0l-5 5m5-5H6"
            />
          </svg>
          該当ページへ移動
        </a>
      </div>

      <!-- Timestamp -->
      <p
        :class="[
          'mt-2 text-xs',
          message.role === 'user' ? 'text-indigo-200' : 'text-gray-500 dark:text-gray-400',
        ]"
      >
        {{ formatTimestamp(message.timestamp) }}
      </p>
    </div>

    <!-- User Avatar -->
    <div
      v-if="message.role === 'user'"
      class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-300 dark:bg-gray-600 flex items-center justify-center"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 text-gray-600 dark:text-gray-300"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
        />
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ChatMessage as ChatMessageType } from '@/types/help'

// Props
interface Props {
  message: ChatMessageType
}

defineProps<Props>()

// Methods
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  })
}
</script>

