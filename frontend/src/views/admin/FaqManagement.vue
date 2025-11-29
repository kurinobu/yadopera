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

    <!-- ローディング表示 -->
    <Loading v-if="loading" />

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchFaqs"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- FAQ一覧 -->
    <FaqList
      v-else
      :faqs="faqs"
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
import { ref, computed, onMounted } from 'vue'
import FaqList from '@/components/admin/FaqList.vue'
import FaqForm from '@/components/admin/FaqForm.vue'
import UnresolvedQuestionsList from '@/components/admin/UnresolvedQuestionsList.vue'
import FaqSuggestionCard from '@/components/admin/FaqSuggestionCard.vue'
import FeedbackLinkedFaqs from '@/components/admin/FeedbackLinkedFaqs.vue'
import Modal from '@/components/common/Modal.vue'
import Loading from '@/components/common/Loading.vue'
import { faqApi } from '@/api/faq'
import { faqSuggestionApi } from '@/api/faqSuggestion'
import type { FAQ, FAQCreate, UnresolvedQuestion, FaqSuggestion, LowRatedAnswer, FAQCategory } from '@/types/faq'

// データ状態
const loading = ref(true)
const error = ref<string | null>(null)
const faqs = ref<FAQ[]>([])

// モックデータ（Week 4でAPI連携に置き換え、一部は残す）
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

// データ取得
const fetchFaqs = async () => {
  try {
    loading.value = true
    error.value = null
    const data = await faqApi.getFaqs()
    faqs.value = data
  } catch (err: any) {
    console.error('Failed to fetch FAQs:', err)
    error.value = err.response?.data?.detail || 'FAQ一覧の取得に失敗しました'
  } finally {
    loading.value = false
  }
}

// コンポーネントマウント時にデータ取得
onMounted(() => {
  fetchFaqs()
})

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

const handleDelete = async (faq: FAQ) => {
  if (!confirm(`FAQ「${faq.question}」を削除しますか？`)) {
    return
  }
  
  try {
    await faqApi.deleteFaq(faq.id)
    // FAQ一覧を再取得
    await fetchFaqs()
  } catch (err: any) {
    console.error('Failed to delete FAQ:', err)
    alert(err.response?.data?.detail || 'FAQの削除に失敗しました')
  }
}

const handleAddFaqFromQuestion = (question: UnresolvedQuestion) => {
  // 未解決質問からFAQ提案を生成
  selectedSuggestion.value = generateSuggestion(question)
}

const handleSubmitFaq = async (data: FAQCreate) => {
  try {
    if (isEditMode.value && editingFaq.value) {
      // FAQ更新
      await faqApi.updateFaq(editingFaq.value.id, data)
    } else {
      // FAQ作成
      await faqApi.createFaq(data)
    }
    
    // FAQ一覧を再取得
    await fetchFaqs()
    handleCloseForm()
  } catch (err: any) {
    console.error('Failed to save FAQ:', err)
    alert(err.response?.data?.detail || 'FAQの保存に失敗しました')
  }
}

const handleCloseForm = () => {
  showAddForm.value = false
  editingFaq.value = null
}

const handleApproveSuggestion = async (suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリアしてFAQ一覧を再取得
  selectedSuggestion.value = null
  await fetchFaqs()
}

const handleRejectSuggestion = async (suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリア
  selectedSuggestion.value = null
}

const handleFeedbackImprove = async (answer: LowRatedAnswer) => {
  try {
    // FAQ提案を生成（GPT-4o mini）
    const suggestion = await faqSuggestionApi.generateSuggestion(answer.message_id)
    selectedSuggestion.value = suggestion
  } catch (err: any) {
    console.error('Failed to generate FAQ suggestion:', err)
    alert(err.response?.data?.detail || 'FAQ提案の生成に失敗しました')
  }
}

const handleFeedbackIgnore = (answer: LowRatedAnswer) => {
  // TODO: Week 4でAPI連携を実装（ステップ4で実装予定）
  console.log('Feedback ignore:', answer)
}
</script>

<style scoped>
/* Component styles */
</style>

