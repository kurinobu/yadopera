<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            未解決質問リスト
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            エスカレーションされた質問
          </p>
        </div>
        <span
          v-if="questions.length > 0"
          class="px-3 py-1 text-sm font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full"
        >
          {{ questions.length }}件
        </span>
      </div>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="question in questions"
        :key="question.id"
        class="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-2">
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded',
                  getLanguageBadgeClass(question.language)
                ]"
              >
                {{ getLanguageLabel(question.language) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                信頼度: {{ formatConfidence(question.confidence_score) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatRelativeTime(question.created_at) }}
              </span>
            </div>
            <p class="text-sm font-medium text-gray-900 dark:text-white">
              {{ question.question }}
            </p>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              @click="handleAddFaq(question)"
              class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
            >
              FAQ追加
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="questions.length === 0"
        class="px-6 py-12 text-center"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          未解決質問はありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { formatRelativeTime, formatConfidence } from '@/utils/formatters'
import type { UnresolvedQuestion } from '@/types/faq'

interface Props {
  questions: UnresolvedQuestion[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'add-faq': [question: UnresolvedQuestion]
}>()

const handleAddFaq = (question: UnresolvedQuestion) => {
  emit('add-faq', question)
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

