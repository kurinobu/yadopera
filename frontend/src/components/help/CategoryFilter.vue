<template>
  <div class="flex flex-wrap gap-2">
    <button
      v-for="category in categories"
      :key="category"
      @click="handleCategoryClick(category)"
      :class="[
        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
        selectedCategory === category
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
      ]"
    >
      {{ getCategoryLabel(category) }}
    </button>
    <button
      @click="handleCategoryClick(null)"
      :class="[
        'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
        selectedCategory === null
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
      ]"
    >
      すべて
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHelpStore } from '@/stores/help'
import type { FaqCategory } from '@/types/help'

const helpStore = useHelpStore()

const categories = computed(() => helpStore.categories)
const selectedCategory = computed(() => helpStore.selectedCategory)

const getCategoryLabel = (category: string): string => {
  const labels: Record<string, string> = {
    setup: '初期設定',
    qrcode: 'QRコード',
    faq_management: 'FAQ管理',
    ai_logic: 'AI仕組み',
    logs: 'ログ分析',
    troubleshooting: 'トラブルシューティング',
    billing: '料金',
    security: 'セキュリティ',
  }
  return labels[category] || category
}

const handleCategoryClick = (category: string | null) => {
  helpStore.setCategory(category as FaqCategory | null)
  helpStore.fetchFaqs(category || undefined)
}
</script>

