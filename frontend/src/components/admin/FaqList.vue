<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
    <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
          FAQ一覧
        </h3>
        <div class="flex items-center space-x-2">
          <select
            v-model="selectedCategory"
            class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">すべてのカテゴリ</option>
            <option value="basic">Basic</option>
            <option value="facilities">Facilities</option>
            <option value="location">Location</option>
            <option value="trouble">Trouble</option>
          </select>
        </div>
      </div>
    </div>

    <div class="divide-y divide-gray-200 dark:divide-gray-700">
      <template v-for="category in categories" :key="category">
        <div
          v-if="getFaqsByCategory(category).length > 0"
          class="p-6"
        >
          <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
            {{ getCategoryLabel(category) }} ({{ getFaqsByCategory(category).length }}件)
          </h4>
          <div class="space-y-4">
            <div
              v-for="faq in getFaqsByCategory(category)"
              :key="faq.id"
              class="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-2">
                    <span
                      :class="[
                        'px-2 py-1 text-xs font-medium rounded',
                        getCategoryBadgeClass(category)
                      ]"
                    >
                      {{ getCategoryLabel(category) }}
                    </span>
                    <span
                      v-if="!faq.is_active"
                      class="px-2 py-1 text-xs font-medium bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded"
                    >
                      無効
                    </span>
                    <span class="text-xs text-gray-500 dark:text-gray-400">
                      優先度: {{ faq.priority }}
                    </span>
                  </div>
                  <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">
                    Q: {{ faq.question }}
                  </p>
                  <p class="text-sm text-gray-700 dark:text-gray-300">
                    A: {{ faq.answer }}
                  </p>
                </div>
                <div class="ml-4 flex-shrink-0 flex items-center space-x-2">
                  <button
                    @click="handleEdit(faq)"
                    class="px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
                  >
                    編集
                  </button>
                  <button
                    @click="handleDelete(faq)"
                    class="px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
                  >
                    削除
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <div
        v-if="filteredFaqs.length === 0"
        class="px-6 py-12 text-center"
      >
        <p class="text-sm text-gray-500 dark:text-gray-400">
          FAQがありません
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { FAQ, FAQCategory } from '@/types/faq'

interface Props {
  faqs: FAQ[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  edit: [faq: FAQ]
  delete: [faq: FAQ]
}>()

const selectedCategory = ref<FAQCategory | ''>('')

const categories: FAQCategory[] = ['basic', 'facilities', 'location', 'trouble']

const filteredFaqs = computed(() => {
  if (!selectedCategory.value) {
    return props.faqs
  }
  return props.faqs.filter(faq => faq.category === selectedCategory.value)
})

const getFaqsByCategory = (category: FAQCategory): FAQ[] => {
  return filteredFaqs.value.filter(faq => faq.category === category)
}

const getCategoryLabel = (category: FAQCategory): string => {
  const labels: Record<FAQCategory, string> = {
    basic: 'Basic',
    facilities: 'Facilities',
    location: 'Location',
    trouble: 'Trouble'
  }
  return labels[category]
}

const getCategoryBadgeClass = (category: FAQCategory): string => {
  const classes: Record<FAQCategory, string> = {
    basic: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    facilities: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    location: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    trouble: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  return classes[category]
}

const handleEdit = (faq: FAQ) => {
  emit('edit', faq)
}

const handleDelete = (faq: FAQ) => {
  if (confirm(`「${faq.question}」を削除しますか？`)) {
    emit('delete', faq)
  }
}
</script>

<style scoped>
/* Component styles */
</style>

