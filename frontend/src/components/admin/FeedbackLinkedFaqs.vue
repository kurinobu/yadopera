<template>
  <div id="feedback-linked-faqs" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        ゲストフィードバック連動FAQ
      </h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        👎評価が2回以上ついた回答
      </p>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="answer in lowRatedFaqs"
        :key="answer.message_id"
        class="px-6 py-4 bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-2">
              <span class="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
                👎 {{ answer.negative_count }}回
              </span>
            </div>
            <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
              Q: {{ answer.question }}
            </p>
            <p class="text-sm text-gray-700 dark:text-gray-300">
              A: {{ answer.answer }}
            </p>
          </div>
        </div>
        <div class="flex items-center space-x-2 mt-4">
          <button
            @click="handleImprove(answer)"
            class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
          >
            FAQ改善提案
          </button>
          <button
            @click="handleIgnore(answer)"
            class="px-3 py-1.5 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            無視
          </button>
        </div>
      </div>

      <div
        v-if="lowRatedFaqs.length === 0"
        class="px-6 py-12 text-center"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          低評価回答はありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LowRatedAnswer } from '@/types/faq'

interface Props {
  lowRatedFaqs: LowRatedAnswer[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  improve: [answer: LowRatedAnswer]
  ignore: [answer: LowRatedAnswer]
}>()

const handleImprove = (answer: LowRatedAnswer) => {
  emit('improve', answer)
}

const handleIgnore = (answer: LowRatedAnswer) => {
  emit('ignore', answer)
}
</script>

<style scoped>
/* Component styles */
</style>

