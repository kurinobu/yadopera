<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      スタッフ対応が必要だった質問
    </h3>
    
    <div class="text-center">
      <p class="text-3xl font-bold text-gray-900 dark:text-white">
        {{ data.total }}件
      </p>
      
      <div class="mt-4 space-y-2">
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600 dark:text-gray-400">未解決</span>
          <span 
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              data.unresolved > 0 
                ? 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200' 
                : 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200'
            ]"
          >
            {{ data.unresolved }}件
          </span>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-sm text-gray-600 dark:text-gray-400">解決済み</span>
          <span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full text-sm font-semibold">
            {{ data.resolved }}件
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EscalationsSummary } from '@/types/dashboard'

interface Props {
  data: EscalationsSummary
}

defineProps<Props>()
</script>

<style scoped>
/* Component styles */
</style>

