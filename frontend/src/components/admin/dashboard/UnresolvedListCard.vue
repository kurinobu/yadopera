<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
      未解決の質問
    </h3>
    
    <div v-if="escalations.length === 0" class="text-center py-8">
      <p class="text-gray-500 dark:text-gray-400">未解決の質問はありません</p>
    </div>
    
    <div v-else class="space-y-3">
      <div
        v-for="escalation in escalations"
        :key="escalation.id"
        @click="handleClick(escalation)"
        :class="[
          'p-4 border rounded-lg transition-colors',
          escalation.session_id 
            ? 'border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer'
            : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 cursor-not-allowed opacity-60'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <p class="text-sm text-gray-900 dark:text-white line-clamp-2">
              {{ escalation.message || 'メッセージなし' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {{ formatDate(escalation.created_at) }}
            </p>
            <!-- session_idが空文字列の場合の警告表示 -->
            <p v-if="!escalation.session_id" class="text-xs text-red-600 dark:text-red-400 mt-1">
              ⚠️ 会話詳細を表示できません（データ不整合）
            </p>
          </div>
          <svg 
            v-if="escalation.session_id"
            class="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { UnresolvedEscalation } from '@/types/dashboard'

interface Props {
  escalations: UnresolvedEscalation[]
}

const props = defineProps<Props>()
const router = useRouter()

const handleClick = (escalation: UnresolvedEscalation) => {
  // session_idが空文字列の場合は遷移しない
  if (!escalation.session_id) {
    console.warn(`Cannot navigate: session_id is empty for escalation ${escalation.id}`)
    return
  }
  
  router.push({
    name: 'ConversationDetail',
    params: { session_id: escalation.session_id }
  })
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('ja-JP', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

