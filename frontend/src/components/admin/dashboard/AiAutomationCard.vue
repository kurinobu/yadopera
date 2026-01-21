<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      AI自動応答数
    </h3>
    
    <div class="text-center">
      <p class="text-3xl font-bold text-gray-900 dark:text-white">
        {{ data.ai_responses }}件
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        自動化率: {{ data.automation_rate.toFixed(1) }}%
      </p>
      
      <!-- プログレスバー -->
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mt-4">
        <div 
          class="h-2 rounded-full transition-all bg-green-600 dark:bg-green-500"
          :style="{ width: Math.min(100, data.automation_rate) + '%' }"
        ></div>
      </div>
      
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">
        総質問数: {{ data.total_questions }}件
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AiAutomation } from '@/types/dashboard'

interface Props {
  data: AiAutomation
}

defineProps<Props>()
</script>

<style scoped>
/* Component styles */
</style>

