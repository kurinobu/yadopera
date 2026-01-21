<template>
  <div
    class="
      p-4 rounded-lg border border-gray-200 dark:border-gray-700
      hover:border-indigo-300 hover:shadow-md dark:hover:border-indigo-600
      transition-all cursor-pointer
      bg-white dark:bg-gray-800
    "
    @click="toggleExpanded"
  >
    <!-- Question -->
    <div class="flex items-start justify-between">
      <h3 class="flex-1 text-base font-medium text-gray-900 dark:text-white" v-html="highlightedQuestion"></h3>
      <button
        class="ml-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
        :aria-label="isExpanded ? '閉じる' : '開く'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5 transition-transform"
          :class="{ 'rotate-180': isExpanded }"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
    </div>

    <!-- Category Badge -->
    <div class="mt-2">
      <span
        class="
          inline-block px-2 py-1 text-xs font-medium rounded
          bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200
        "
      >
        {{ categoryLabel }}
      </span>
    </div>

    <!-- Answer (Expandable) -->
    <Transition name="expand">
      <div v-if="isExpanded" class="mt-4 space-y-3">
        <div class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap" v-html="highlightedAnswer"></div>

        <!-- Related URL -->
        <div v-if="faq.related_url" class="pt-3 border-t border-gray-200 dark:border-gray-700">
          <a
            :href="faq.related_url"
            class="
              inline-flex items-center text-sm text-indigo-600 dark:text-indigo-400
              hover:text-indigo-800 dark:hover:text-indigo-300 hover:underline
            "
            @click.stop
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-4 w-4 mr-1"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 7l5 5m0 0l-5 5m5-5H6"
              />
            </svg>
            該当ページへ移動
          </a>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Faq } from '@/types/help'

// Props
interface Props {
  faq: Faq
  highlightQuery?: string
}

const props = defineProps<Props>()

// State
const isExpanded = ref(false)

// Computed
const categoryLabel = computed(() => {
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
  return labels[props.faq.category] || props.faq.category
})

const highlightedQuestion = computed(() => {
  return highlightText(props.faq.question, props.highlightQuery)
})

const highlightedAnswer = computed(() => {
  return highlightText(props.faq.answer, props.highlightQuery)
})

// Methods
const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}

const highlightText = (text: string, query?: string): string => {
  if (!query || query.trim().length === 0) {
    return text
  }

  const regex = new RegExp(`(${escapeRegex(query)})`, 'gi')
  return text.replace(regex, '<mark class="bg-yellow-200 dark:bg-yellow-800">$1</mark>')
}

const escapeRegex = (str: string): string => {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}
</script>

<style scoped>
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 500px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>

