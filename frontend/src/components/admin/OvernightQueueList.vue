<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            スタッフ不在時間帯対応キュー
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            スタッフ不在時間帯にエスカレーションされた質問
          </p>
        </div>
        <div class="flex items-center space-x-2">
          <span
            v-if="queue.length > 0"
            class="px-3 py-1 text-sm font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200 rounded-full"
          >
            {{ queue.length }}件
          </span>
          <button
            v-if="queue.length > 0"
            @click="handleViewAll"
            class="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
          >
            対応する
          </button>
        </div>
      </div>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <div
        v-for="item in queue"
        :key="item.id"
        :class="[
          'px-6 py-4',
          item.resolved_at ? 'bg-gray-50 dark:bg-gray-900 opacity-60' : 'hover:bg-gray-50 dark:hover:bg-gray-700',
          'transition-colors'
        ]"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1 min-w-0">
            <div class="flex items-center space-x-2 mb-2">
              <span
                :class="[
                  'px-2 py-1 text-xs font-medium rounded',
                  getLanguageBadgeClass(item.language)
                ]"
              >
                {{ getLanguageLabel(item.language) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">
                {{ formatRelativeTime(item.created_at) }}
              </span>
              <span
                v-if="item.resolved_at"
                class="px-2 py-1 text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded"
              >
                対応済み
              </span>
            </div>
            <p class="text-sm text-gray-900 dark:text-white font-medium mb-2">
              {{ item.guest_message }}
            </p>
            <div class="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
              <span>
                対応予定: {{ formatDateTime(item.scheduled_notify_at) }}
              </span>
            </div>
          </div>
          <div class="ml-4 flex-shrink-0">
            <button
              v-if="!item.resolved_at && showResolveButton"
              @click="handleResolve(item)"
              class="px-3 py-1.5 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
            >
              対応済み
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="queue.length === 0"
        class="px-6 py-12 text-center"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          スタッフ不在時間帯対応キューはありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { formatRelativeTime, formatDateTime } from '@/utils/formatters'
import type { OvernightQueue } from '@/types/dashboard'

interface Props {
  queue: OvernightQueue[]
  showResolveButton?: boolean  // 対応済みボタンを表示するか（専用ページ用）
}

const props = withDefaults(defineProps<Props>(), {
  showResolveButton: false
})

const router = useRouter()

const emit = defineEmits<{
  viewAll: []
  resolve: [item: OvernightQueue]
}>()

const handleViewAll = () => {
  // 夜間対応キュー専用ページに遷移（ゲストフィードバック集計の「対応する」ボタンと同じパターン）
  router.push('/admin/overnight-queue')
  emit('viewAll')
}

const handleResolve = (item: OvernightQueue) => {
  emit('resolve', item)
}

const getLanguageLabel = (lang: string | undefined): string => {
  if (!lang) return '不明'  // undefinedの場合のデフォルト値
  
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

const getLanguageBadgeClass = (lang: string | undefined): string => {
  if (!lang) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'  // undefinedの場合のデフォルト値
  
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

