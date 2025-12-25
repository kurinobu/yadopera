<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
    <div class="flex items-start justify-between mb-4">
      <div class="flex-1">
        <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">
          FAQ追加提案
        </h4>
        <p class="text-xs text-gray-500 dark:text-gray-400">
          {{ formatRelativeTime(suggestion.created_at) }}
        </p>
      </div>
      <span
        :class="[
          'px-2 py-1 text-xs font-medium rounded',
          getStatusBadgeClass(suggestion.status)
        ]"
      >
        {{ getStatusLabel(suggestion.status) }}
      </span>
    </div>

    <div class="space-y-4">
      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          質問文
        </label>
        <Input
          v-model="editedQuestion"
          type="textarea"
          :rows="2"
          placeholder="質問文を入力"
          :maxlength="200"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          回答文（テンプレート）
        </label>
        <Input
          v-model="editedAnswer"
          type="textarea"
          :rows="3"
          placeholder="回答文を入力"
          :maxlength="200"
        />
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          GPT-4o miniで自動生成されたテンプレート（編集可能）
        </p>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          カテゴリ
        </label>
        <select
          v-model="editedCategory"
          class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="basic">Basic</option>
          <option value="facilities">Facilities</option>
          <option value="location">Location</option>
          <option value="trouble">Trouble</option>
        </select>
        <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
          自動推定されたカテゴリ（編集可能）
        </p>
      </div>
    </div>

    <div class="flex items-center justify-end space-x-3 mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
      <button
        @click="handleCancel"
        :disabled="loading"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        キャンセル
      </button>
      <button
        @click="handleReject"
        :disabled="loading || suggestion.status !== 'pending'"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? '処理中...' : '却下' }}
      </button>
      <button
        @click="handleApprove"
        :disabled="loading || suggestion.status !== 'pending'"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ loading ? '処理中...' : '承認してFAQ追加' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import Input from '@/components/common/Input.vue'
import { formatRelativeTime } from '@/utils/formatters'
import { faqSuggestionApi } from '@/api/faqSuggestion'
import type { FaqSuggestion, FAQCategory } from '@/types/faq'

interface Props {
  suggestion: FaqSuggestion
}

const props = defineProps<Props>()

const emit = defineEmits<{
  approve: [suggestion: FaqSuggestion]
  reject: [suggestion: FaqSuggestion]
  cancel: [suggestion: FaqSuggestion]
}>()

const loading = ref(false)

const editedQuestion = ref(props.suggestion.suggested_question)
const editedAnswer = ref(props.suggestion.suggested_answer)
const editedCategory = ref<FAQCategory>(props.suggestion.suggested_category)

watch(() => props.suggestion, (suggestion) => {
  editedQuestion.value = suggestion.suggested_question
  editedAnswer.value = suggestion.suggested_answer
  editedCategory.value = suggestion.suggested_category
}, { immediate: true })

const getStatusLabel = (status: string): string => {
  const labels: Record<string, string> = {
    pending: '承認待ち',
    approved: '承認済み',
    rejected: '却下済み'
  }
  return labels[status] || status
}

const getStatusBadgeClass = (status: string): string => {
  const classes: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const handleApprove = async () => {
  if (loading.value) return
  
  try {
    loading.value = true
    await faqSuggestionApi.approveSuggestion(props.suggestion.id, {
      question: editedQuestion.value,
      answer: editedAnswer.value,
      category: editedCategory.value,
      priority: 1
    })
    emit('approve', props.suggestion)
  } catch (err: any) {
    console.error('Failed to approve suggestion:', err)
    alert(err.response?.data?.detail || '提案の承認に失敗しました')
  } finally {
    loading.value = false
  }
}

const handleReject = async () => {
  if (loading.value) return
  
  if (!confirm('この提案を却下しますか？')) {
    return
  }
  
  try {
    loading.value = true
    await faqSuggestionApi.rejectSuggestion(props.suggestion.id)
    emit('reject', props.suggestion)
  } catch (err: any) {
    console.error('Failed to reject suggestion:', err)
    alert(err.response?.data?.detail || '提案の却下に失敗しました')
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  if (loading.value) return
  emit('cancel', props.suggestion)
}
</script>

<style scoped>
/* Component styles */
</style>

