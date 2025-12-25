<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
          FAQ管理
        </h1>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
          FAQの追加・編集・削除と自動学習機能
        </p>
      </div>
      <button
        @click="showAddForm = true"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
      >
        + 新規FAQ追加
      </button>
    </div>

    <!-- FAQ一覧 -->
    <FaqList
      :faqs="mockFaqs"
      @edit="handleEdit"
      @delete="handleDelete"
    />

    <!-- 未解決質問リスト -->
    <UnresolvedQuestionsList
      :questions="mockUnresolvedQuestions"
      @add-faq="handleAddFaqFromQuestion"
    />

    <!-- FAQ自動学習UI -->
    <div v-if="selectedSuggestion" class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        FAQ追加提案
      </h2>
      <FaqSuggestionCard
        :suggestion="selectedSuggestion"
        @approve="handleApproveSuggestion"
        @reject="handleRejectSuggestion"
      />
    </div>

    <!-- ゲストフィードバック連動 -->
    <FeedbackLinkedFaqs
      :low-rated-faqs="mockLowRatedAnswers"
      @improve="handleFeedbackImprove"
      @ignore="handleFeedbackIgnore"
    />

    <!-- FAQ追加・編集モーダル -->
    <Modal
      v-model="showAddForm"
      :title="isEditMode ? 'FAQ編集' : 'FAQ追加'"
      size="lg"
      @close="handleCloseForm"
    >
      <FaqForm
        :faq="editingFaq"
        @submit="handleSubmitFaq"
        @cancel="handleCloseForm"
      />
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import FaqList from '@/components/admin/FaqList.vue'
import FaqForm from '@/components/admin/FaqForm.vue'
import UnresolvedQuestionsList from '@/components/admin/UnresolvedQuestionsList.vue'
import FaqSuggestionCard from '@/components/admin/FaqSuggestionCard.vue'
import FeedbackLinkedFaqs from '@/components/admin/FeedbackLinkedFaqs.vue'
import Modal from '@/components/common/Modal.vue'
import type { FAQ, FAQCreate, UnresolvedQuestion, FaqSuggestion, LowRatedAnswer, FAQCategory } from '@/types/faq'

// モックデータ（Week 4でAPI連携に置き換え）
const mockFaqs: FAQ[] = [
  {
    id: 1,
    facility_id: 1,
    category: 'basic',
    language: 'en',
    question: 'What time is check-in?',
    answer: 'Check-in is from 3pm to 10pm. If you arrive outside these hours, please contact us in advance.',
    priority: 5,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 2,
    facility_id: 1,
    category: 'basic',
    language: 'en',
    question: 'What is the WiFi password?',
    answer: 'The WiFi password is guest2024. The SSID is TokyoGuesthouse_WiFi.',
    priority: 5,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: 3,
    facility_id: 1,
    category: 'facilities',
    language: 'en',
    question: 'Where is the laundry room?',
    answer: 'The laundry room is on the 2nd floor. Washing machines are available 24/7.',
    priority: 3,
    is_active: true,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
]

const mockUnresolvedQuestions: UnresolvedQuestion[] = [
  {
    id: 1,
    message_id: 101,
    facility_id: 1,
    question: 'Late checkout possible?',
    language: 'en',
    confidence_score: 0.65,
    created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString()
  },
  {
    id: 2,
    message_id: 102,
    facility_id: 1,
    question: 'タオルはどこにありますか？',
    language: 'ja',
    confidence_score: 0.58,
    created_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString()
  }
]

const mockLowRatedAnswers: LowRatedAnswer[] = [
  {
    message_id: 201,
    question: 'WiFi password?',
    answer: 'The password is guest2024.',
    negative_count: 3
  },
  {
    message_id: 202,
    question: 'Check-in time?',
    answer: 'Check-in is from 3pm to 10pm.',
    negative_count: 2
  }
]

// 状態管理
const showAddForm = ref(false)
const editingFaq = ref<FAQ | null>(null)
const selectedSuggestion = ref<FaqSuggestion | null>(null)

const isEditMode = computed(() => !!editingFaq.value)

// モックのFAQ提案（未解決質問から生成）
const generateSuggestion = (question: UnresolvedQuestion): FaqSuggestion => {
  // モック: 回答テンプレート自動生成（Week 4でAPI連携）
  const mockAnswer = `This is a suggested answer template for: ${question.question}. Please customize this answer.`
  
  // モック: カテゴリ自動推定（Week 4でAPI連携）
  const mockCategory: FAQCategory = 'basic'
  
  return {
    id: question.id,
    facility_id: question.facility_id,
    source_message_id: question.message_id,
    suggested_question: question.question,
    suggested_answer: mockAnswer,
    suggested_category: mockCategory,
    status: 'pending',
    created_at: question.created_at
  }
}

// イベントハンドラー
const handleEdit = (faq: FAQ) => {
  editingFaq.value = faq
  showAddForm.value = true
}

const handleDelete = (faq: FAQ) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Delete FAQ:', faq)
}

const handleAddFaqFromQuestion = (question: UnresolvedQuestion) => {
  // 未解決質問からFAQ提案を生成
  selectedSuggestion.value = generateSuggestion(question)
}

const handleSubmitFaq = (data: FAQCreate) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Submit FAQ:', data, isEditMode.value ? 'edit' : 'create')
  handleCloseForm()
}

const handleCloseForm = () => {
  showAddForm.value = false
  editingFaq.value = null
}

const handleApproveSuggestion = (
  suggestion: FaqSuggestion,
  edited: { question: string; answer: string; category: FAQCategory }
) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Approve suggestion:', suggestion, edited)
  selectedSuggestion.value = null
}

const handleRejectSuggestion = (suggestion: FaqSuggestion) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Reject suggestion:', suggestion)
  selectedSuggestion.value = null
}

const handleFeedbackImprove = (answer: LowRatedAnswer) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Feedback improve:', answer)
}

const handleFeedbackIgnore = (answer: LowRatedAnswer) => {
  // TODO: Week 4でAPI連携を実装
  console.log('Feedback ignore:', answer)
}

const isEditMode = computed(() => !!editingFaq.value)
</script>

<style scoped>
/* Component styles */
</style>

