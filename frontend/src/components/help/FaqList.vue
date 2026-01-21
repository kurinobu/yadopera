<template>
  <div class="space-y-4">
    <!-- Loading State -->
    <div v-if="helpStore.isLoading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      <p class="mt-4 text-sm text-gray-600 dark:text-gray-400">読み込み中...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="displayFaqs.length === 0" class="text-center py-12">
      <p class="text-lg font-medium text-gray-900 dark:text-white">該当するFAQが見つかりませんでした</p>
      <button
        @click="handleRetry"
        class="mt-4 px-4 py-2 text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300"
      >
        再試行
      </button>
    </div>

    <!-- FAQ Items -->
    <div v-else class="space-y-3">
      <FaqItem
        v-for="faq in displayFaqs"
        :key="faq.id"
        :faq="faq"
        :highlight-query="helpStore.searchQuery"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useHelpStore } from '@/stores/help'
import FaqItem from './FaqItem.vue'

const helpStore = useHelpStore()

const displayFaqs = computed(() => {
  if (helpStore.hasSearchResults) {
    return helpStore.searchResults
  }
  return helpStore.filteredFaqs
})

const handleRetry = async () => {
  await helpStore.fetchFaqs(helpStore.selectedCategory || undefined)
}
</script>

