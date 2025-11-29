<template>
  <div class="mb-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      よくある質問 / Frequently Asked Questions
    </h3>
    <div v-if="questions.length > 0" class="space-y-3">
      <button
        v-for="question in questions"
        :key="question.id"
        @click="handleQuestionClick(question)"
        class="w-full text-left p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-600 hover:shadow-md transition-all"
      >
        <div class="flex items-start justify-between">
          <p class="text-sm font-medium text-gray-900 dark:text-white flex-1">
            {{ question.question }}
          </p>
          <svg
            class="w-5 h-5 text-gray-400 flex-shrink-0 ml-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </button>
    </div>
    <div v-else class="text-center py-8 text-gray-500 dark:text-gray-400">
      <p class="text-sm">よくある質問はありません</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TopQuestion } from '@/types/facility'

interface Props {
  questions: TopQuestion[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  questionClick: [question: TopQuestion]
}>()

const handleQuestionClick = (question: TopQuestion) => {
  emit('questionClick', question)
}
</script>

<style scoped>
/* Component styles */
</style>

