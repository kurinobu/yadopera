<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
        今月の質問数
      </h3>
      <span :class="planTypeBadgeClass" class="px-3 py-1 text-xs font-semibold rounded-full">
        {{ planTypeLabel }}
      </span>
    </div>
    
    <!-- Freeプラン：30件超過後 -->
    <div v-if="data.plan_type === 'Free' && data.status === 'faq_only'" class="text-center">
      <p class="text-3xl font-bold text-red-600 dark:text-red-400">
        {{ data.current_month_questions }}件
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
        30件超過：FAQのみ対応中
      </p>
      <span class="inline-block mt-2 px-3 py-1 bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 text-xs rounded-full">
        FAQのみ対応中
      </span>
    </div>
    
    <!-- Freeプラン：通常時（30件以内） -->
    <div v-else-if="data.plan_type === 'Free' && data.status === 'normal'">
      <div class="flex items-end justify-between mb-2">
        <p class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ data.current_month_questions }}
        </p>
        <p class="text-gray-500 dark:text-gray-400">
          / {{ data.plan_limit }}件
        </p>
      </div>
      
      <!-- プログレスバー -->
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
        <div 
          class="h-2 rounded-full transition-all"
          :class="progressBarColor"
          :style="{ width: Math.min(100, (data.usage_percentage || 0)) + '%' }"
        ></div>
      </div>
      
      <!-- ステータスメッセージ -->
      <p v-if="statusMessage" :class="statusTextColor" class="text-sm">
        {{ statusMessage }}
      </p>
    </div>
    
    <!-- Miniプラン：従量課金のみ -->
    <div v-else-if="data.plan_type === 'Mini'" class="text-center">
      <p class="text-3xl font-bold text-gray-900 dark:text-white">
        {{ data.current_month_questions }}件
      </p>
      <span class="inline-block mt-2 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
        従量課金プラン
      </span>
    </div>
    
    <!-- Small/Standard/Premium：プログレスバー表示 -->
    <div v-else>
      <div class="flex items-end justify-between mb-2">
        <p class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ data.current_month_questions }}
        </p>
        <p class="text-gray-500 dark:text-gray-400">
          / {{ data.plan_limit }}件
        </p>
      </div>
      
      <!-- プログレスバー -->
      <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mb-2">
        <div 
          class="h-2 rounded-full transition-all"
          :class="progressBarColor"
          :style="{ width: Math.min(100, (data.usage_percentage || 0)) + '%' }"
        ></div>
      </div>
      
      <!-- ステータスメッセージ -->
      <p v-if="statusMessage" :class="statusTextColor" class="text-sm">
        {{ statusMessage }}
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { MonthlyUsage } from '@/types/dashboard'

interface Props {
  data: MonthlyUsage
}

const props = defineProps<Props>()

// プラン名ラベル
const planTypeLabel = computed(() => {
  const labels = {
    'Free': 'Freeプラン',
    'Mini': 'Miniプラン',
    'Small': 'Smallプラン',
    'Standard': 'Standardプラン',
    'Premium': 'Premiumプラン'
  }
  return labels[props.data.plan_type as keyof typeof labels] || props.data.plan_type
})

// プラン名バッジのスタイル
const planTypeBadgeClass = computed(() => {
  const classes = {
    'Free': 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200',
    'Mini': 'bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200',
    'Small': 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200',
    'Standard': 'bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200',
    'Premium': 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200'
  }
  return classes[props.data.plan_type as keyof typeof classes] || 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200'
})

const progressBarColor = computed(() => {
  const usage = props.data.usage_percentage || 0
  if (usage >= 100) return 'bg-red-600 dark:bg-red-500'
  if (usage >= 91) return 'bg-orange-600 dark:bg-orange-500'
  if (usage >= 71) return 'bg-yellow-500 dark:bg-yellow-400'
  return 'bg-green-600 dark:bg-green-500'
})

const statusTextColor = computed(() => {
  const usage = props.data.usage_percentage || 0
  if (usage >= 100) return 'text-red-600 dark:text-red-400 font-semibold'
  if (usage >= 91) return 'text-orange-600 dark:text-orange-400 font-semibold'
  if (usage >= 71) return 'text-yellow-600 dark:text-yellow-400'
  return 'text-green-600 dark:text-green-400'
})

const statusMessage = computed(() => {
  // Miniプランの場合はメッセージを表示しない
  if (props.data.plan_type === 'Mini') {
    return ''
  }
  
  // remaining_questionsがnullの場合はメッセージを表示しない
  if (props.data.remaining_questions === null || props.data.remaining_questions === undefined) {
    return ''
  }
  
  const usage = props.data.usage_percentage || 0
  if (usage >= 100) {
    return `⚠️ 従量課金が発生しています（${props.data.overage_questions}件超過）`
  }
  if (usage >= 91) {
    return `⚠️ まもなく上限です（残り${props.data.remaining_questions}件）`
  }
  if (usage >= 71) {
    return `残り${props.data.remaining_questions}件です`
  }
  return `あと${props.data.remaining_questions}件で上限です`
})
</script>

<style scoped>
/* Component styles */
</style>

