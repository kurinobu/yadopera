<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        リアルタイムチャット履歴
      </h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        最新10件の会話
      </p>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="conversation in conversations"
        :key="conversation.session_id"
        class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
        @click="handleClick(conversation)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-2">
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded',
                  getLanguageBadgeClass(conversation.guest_language)
                ]"
              >
                {{ getLanguageLabel(conversation.guest_language) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatRelativeTime(conversation.created_at) }}
              </span>
            </div>
            <p class="text-sm text-gray-900 dark:text-white font-medium mb-1">
              {{ conversation.last_message }}
            </p>
            <div class="flex items-center space-x-4 mt-2">
              <span class="text-xs text-gray-500 dark:text-gray-400">
                信頼度: {{ formatConfidence(conversation.ai_confidence) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="conversations.length === 0"
        class="px-6 py-12 text-center"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          チャット履歴がありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatRelativeTime, formatConfidence } from '@/utils/formatters'
import type { ChatHistory } from '@/types/dashboard'

interface Props {
  conversations: ChatHistory[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [conversation: ChatHistory]
}>()

const handleClick = (conversation: ChatHistory) => {
  emit('click', conversation)
}

const getLanguageLabel = (lang: string): string => {
  const labels: Record<string, string> = {
    en: '英語',
    ja: '日本語',
    'zh-TW': '繁体中国語',
    'zh-CN': '簡体中国語',
    ko: '韓国語',
    fr: 'フランス語'
  }
  return labels[lang] || lang.toUpperCase()
}

const getLanguageBadgeClass = (lang: string): string => {
  const classes: Record<string, string> = {
    en: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    ja: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    'zh-TW': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'zh-CN': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    ko: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    fr: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-200'
  }
  return classes[lang] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}
</script>

<style scoped>
/* Component styles */
</style>

