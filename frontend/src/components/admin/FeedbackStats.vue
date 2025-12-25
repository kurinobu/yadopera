<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        ゲストフィードバック集計
      </h3>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        👍👎の比率と低評価回答
      </p>
    </div>

    <div class="p-6">
      <!-- フィードバック比率 -->
      <div class="mb-6">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700 dark:text-gray-300">
            肯定率
          </span>
          <span class="text-lg font-bold text-gray-900 dark:text-white">
            {{ formatPercentage(stats.positive_rate) }}
          </span>
        </div>
        <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            :style="{ width: `${stats.positive_rate * 100}%` }"
            class="bg-green-500 h-3 rounded-full transition-all duration-300"
          />
        </div>
        <div class="flex items-center justify-between mt-2 text-xs text-gray-500 dark:text-gray-400">
          <span>👍 {{ stats.positive_count }}件</span>
          <span>👎 {{ stats.negative_count }}件</span>
        </div>
      </div>

      <!-- 低評価回答リスト -->
      <div v-if="stats.low_rated_answers.length > 0">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
          低評価回答（👎2回以上）
        </h4>
        <div class="space-y-3">
          <div
            v-for="answer in stats.low_rated_answers"
            :key="answer.message_id"
            class="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <div class="flex items-start justify-between mb-2">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  Q: {{ answer.question }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  A: {{ answer.answer }}
                </p>
              </div>
              <span class="ml-4 px-2 py-1 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded">
                👎 {{ answer.negative_count }}回
              </span>
            </div>
            <div class="flex items-center space-x-2 mt-3">
              <button
                @click="handleRespond(answer)"
                class="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
              >
                対応する
              </button>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="text-center py-8"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          低評価回答はありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { FeedbackStats } from '@/types/dashboard'

interface Props {
  stats: FeedbackStats
}

const props = defineProps<Props>()

const router = useRouter()

const emit = defineEmits<{
  respond: [answer: FeedbackStats['low_rated_answers'][0]]
}>()

const formatPercentage = (value: number): string => {
  return `${Math.round(value * 100)}%`
}

const handleRespond = async (answer: FeedbackStats['low_rated_answers'][0]) => {
  // FAQ管理ページにジャンプ（ハッシュフラグメントを含む）
  await router.push('/admin/faqs#feedback-linked-faqs')
  // 親コンポーネントに通知（必要に応じて）
  emit('respond', answer)
}
</script>

<style scoped>
/* Component styles */
</style>

