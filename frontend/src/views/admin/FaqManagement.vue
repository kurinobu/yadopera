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
      :questions="unresolvedQuestions"
      @add-faq="handleAddFaqFromQuestion"
    />

    <!-- FAQ自動学習UI -->
    <div v-if="selectedSuggestion" id="faq-suggestion" class="space-y-4">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
        FAQ追加提案
      </h2>
      <FaqSuggestionCard
        :suggestion="selectedSuggestion"
        @approve="handleApproveSuggestion"
        @reject="handleRejectSuggestion"
        @cancel="handleCancelSuggestion"
      />
    </div>

    <!-- ゲストフィードバック連動 -->
    <FeedbackLinkedFaqs
      :low-rated-faqs="lowRatedAnswers"
      :ignoring-message-id="ignoringMessageId"
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

    <!-- 無視確認モーダル -->
    <Modal
      v-model="showIgnoreConfirm"
      title="低評価回答の無視"
      size="md"
      @close="showIgnoreConfirm = false"
    >
      <div class="space-y-4">
        <p class="text-gray-700 dark:text-gray-300">
          この低評価回答を無視しますか？無視した回答は画面から非表示になります。
        </p>
        <div class="flex items-center justify-end space-x-3">
          <button
            @click="showIgnoreConfirm = false"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
          >
            キャンセル
          </button>
          <button
            @click="confirmIgnore"
            :disabled="ignoringMessageId !== null"
            class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="ignoringMessageId !== null">処理中...</span>
            <span v-else>無視する</span>
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import FaqList from '@/components/admin/FaqList.vue'
import FaqForm from '@/components/admin/FaqForm.vue'
import UnresolvedQuestionsList from '@/components/admin/UnresolvedQuestionsList.vue'
import FaqSuggestionCard from '@/components/admin/FaqSuggestionCard.vue'
import FeedbackLinkedFaqs from '@/components/admin/FeedbackLinkedFaqs.vue'
import Modal from '@/components/common/Modal.vue'
import Loading from '@/components/common/Loading.vue'
import { faqApi } from '@/api/faq'
import { faqSuggestionApi } from '@/api/faqSuggestion'
import { unresolvedQuestionsApi } from '@/api/unresolvedQuestions'
import { feedbackApi } from '@/api/feedback'
import type { FAQ, FAQCreate, UnresolvedQuestion, FaqSuggestion, LowRatedAnswer } from '@/types/faq'

// データ状態
const loading = ref(true)
const error = ref<string | null>(null)
const faqs = ref<FAQ[]>([])
const unresolvedQuestions = ref<UnresolvedQuestion[]>([])
const loadingUnresolved = ref(false)

// モックデータ（Week 4でAPI連携に置き換え、一部は残す）
/* const mockFaqs: FAQ[] = [
  {
    id: 1,
    facility_id: 1,
    category: 'basic',
    language: 'en',
    question: 'What time is check-out?',
    answer: 'Check-out is by 11:00 AM. If you need to leave later, please contact us in advance.',
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
] */


// 低評価回答リスト
const lowRatedAnswers = ref<LowRatedAnswer[]>([])

// データ取得
const fetchFaqs = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await faqApi.getFaqs()
    const data = response.faqs
    const isInitializing = response.is_initializing
    const total = response.total
    
    console.log('✅ FAQ取得成功:', {
      count: data.length,
      total: total,
      is_initializing: isInitializing,
      categories: {
        basic: data.filter(f => f.category === 'basic').length,
        facilities: data.filter(f => f.category === 'facilities').length,
        location: data.filter(f => f.category === 'location').length,
        trouble: data.filter(f => f.category === 'trouble').length,
      },
      data: data
    })
    
    faqs.value = data
    
    // バックグラウンド処理が進行中の場合、ポーリングを開始
    if (isInitializing && total < 20) {
      const expectedCount = 20
      const pollInterval = 2000 // 2秒ごとにポーリング
      const maxPollTime = 30000 // 最大30秒
      const startTime = Date.now()
      
      const poll = async () => {
        if (Date.now() - startTime > maxPollTime) {
          // タイムアウト: 現在の件数を表示
          console.log('⏱️ ポーリングタイムアウト: 現在の件数を表示', total)
          loading.value = false
          return
        }
        
        try {
          const newResponse = await faqApi.getFaqs()
          const newData = newResponse.faqs
          const newTotal = newResponse.total
          const newIsInitializing = newResponse.is_initializing
          
          console.log('🔄 ポーリング結果:', {
            count: newData.length,
            total: newTotal,
            is_initializing: newIsInitializing
          })
          
          if (!newIsInitializing && newTotal >= expectedCount) {
            // 完了: 最新のデータを表示
            console.log('✅ バックグラウンド処理完了: 最新のデータを表示', newTotal)
            faqs.value = newData
            loading.value = false
          } else {
            // まだ進行中: 再度ポーリング
            setTimeout(poll, pollInterval)
          }
        } catch (err: any) {
          // エラー: 現在の件数を表示
          console.error('❌ ポーリングエラー:', err)
          loading.value = false
        }
      }
      
      // 初回ポーリングを開始
      console.log('🔄 バックグラウンド処理進行中: ポーリングを開始')
      setTimeout(poll, pollInterval)
    } else {
      // 通常の表示
      loading.value = false
    }
  } catch (err: any) {
    console.error('❌ FAQ取得失敗:', err)
    error.value = err.response?.data?.detail || 'FAQ一覧の取得に失敗しました'
    loading.value = false
  }
}

// 未解決質問リスト取得
const fetchUnresolvedQuestions = async () => {
  try {
    loadingUnresolved.value = true
    const data = await unresolvedQuestionsApi.getUnresolvedQuestions()
    unresolvedQuestions.value = data
  } catch (err: any) {
    console.error('Failed to fetch unresolved questions:', err)
    // エラーは表示しない（未解決質問はオプション機能のため）
    unresolvedQuestions.value = []
  } finally {
    loadingUnresolved.value = false
  }
}

// 低評価回答リスト取得
const fetchLowRatedAnswers = async () => {
  try {
    const data = await feedbackApi.getNegativeFeedbacks()
    lowRatedAnswers.value = data
  } catch (err: any) {
    console.error('Failed to fetch low-rated answers:', err)
    // エラーは表示しない（低評価回答はオプション機能のため）
    lowRatedAnswers.value = []
  }
}

const route = useRoute()

// ハッシュフラグメントまたは要素IDに基づいてスクロール
const scrollToSection = async (targetId?: string) => {
  // 複数回nextTickを呼び出して、DOMの更新を確実に待つ
  await nextTick()
  await nextTick()
  // データが読み込まれるまで少し待つ
  await new Promise(resolve => setTimeout(resolve, 800))
  
  // ターゲットIDを決定（引数 > ハッシュフラグメントの順）
  const hash = route.hash || window.location.hash
  const id = targetId || (hash ? hash.replace('#', '') : null)
  
  if (!id) return
  
  // 対応するIDのリスト
  const supportedIds = ['feedback-linked-faqs', 'faq-suggestion']
  if (!supportedIds.includes(id)) return
  
  // getElementByIdで要素を取得
  const element = document.getElementById(id)
  if (element) {
    // 少し上にオフセットを追加（ヘッダーなどのために）
    const offset = 80
    const elementPosition = element.getBoundingClientRect().top + window.pageYOffset
    const offsetPosition = elementPosition - offset
    window.scrollTo({
      top: offsetPosition,
      behavior: 'smooth'
    })
    console.log('[FaqManagement] Scrolled to section:', id, element)
  } else {
    console.warn('[FaqManagement] Element not found for id:', id)
    // 要素が見つからない場合、もう一度試す（最大3回）
    for (let i = 0; i < 3; i++) {
      await new Promise(resolve => setTimeout(resolve, 500))
      const retryElement = document.getElementById(id)
      if (retryElement) {
        const offset = 80
        const elementPosition = retryElement.getBoundingClientRect().top + window.pageYOffset
        const offsetPosition = elementPosition - offset
        window.scrollTo({
          top: offsetPosition,
          behavior: 'smooth'
        })
        console.log('[FaqManagement] Scrolled to section (retry):', id, retryElement)
        break
      }
    }
  }
}

// コンポーネントマウント時にデータ取得
onMounted(async () => {
  await fetchFaqs()
  await fetchUnresolvedQuestions()
  await fetchLowRatedAnswers()
  // ハッシュフラグメントに基づいてスクロール
  await scrollToSection()
})

// ルートのハッシュが変更されたときにもスクロール
watch(() => route.hash, async (newHash, oldHash) => {
  if (newHash && newHash !== oldHash && (newHash === '#feedback-linked-faqs' || newHash === '#faq-suggestion')) {
    await scrollToSection()
  }
}, { immediate: false })

// window.location.hashの変更も監視（Vue Routerがハッシュを正しく処理しない場合のフォールバック）
watch(() => window.location.hash, async (newHash, oldHash) => {
  if (newHash && newHash !== oldHash && (newHash === '#feedback-linked-faqs' || newHash === '#faq-suggestion')) {
    await scrollToSection()
  }
}, { immediate: false })

// 状態管理
const showAddForm = ref(false)
const editingFaq = ref<FAQ | null>(null)
const selectedSuggestion = ref<FaqSuggestion | null>(null)

const isEditMode = computed(() => !!editingFaq.value)

// モックのFAQ提案（未解決質問から生成）
/* const generateSuggestion = (question: UnresolvedQuestion): FaqSuggestion => {
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
} */

// イベントハンドラー
const handleEdit = (faq: FAQ) => {
  editingFaq.value = faq
  showAddForm.value = true
}

const handleDelete = async (faq: FAQ) => {
  // 最初の翻訳の質問文を取得（削除確認メッセージ用）
  const questionText = faq.translations && faq.translations.length > 0
    ? faq.translations[0].question
    : `FAQ ID: ${faq.id}`
  
  if (!confirm(`FAQ「${questionText}」を削除しますか？`)) {
    return
  }
  
  try {
    await faqApi.deleteFaq(faq.id)
    // キャッシュの更新を待つため、少し待ってから再取得
    await new Promise(resolve => setTimeout(resolve, 100))
    // FAQ一覧を再取得
    await fetchFaqs()
    // 成功メッセージ（オプション）
    const questionText = faq.translations && faq.translations.length > 0
      ? faq.translations[0].question
      : `FAQ ID: ${faq.id}`
    console.log(`FAQ「${questionText}」を削除しました`)
  } catch (err: any) {
    console.error('Failed to delete FAQ:', err)
    // エラーメッセージをユーザーフレンドリーに変換
    let errorMessage = 'FAQの削除に失敗しました'
    const detail = err.response?.data?.detail || err.message || ''
    
    if (detail.includes('FAQ not found')) {
      errorMessage = '削除しようとしたFAQが見つかりませんでした。既に削除されている可能性があります。ページをリロードして最新の状態を確認してください。'
    } else if (detail.includes('does not belong to facility')) {
      errorMessage = 'このFAQは削除できません。権限がない可能性があります。'
    } else if (detail) {
      errorMessage = `削除に失敗しました: ${detail}`
    }
    
    alert(errorMessage)
    // エラーが発生しても、FAQ一覧を再取得（キャッシュの問題を回避）
    await fetchFaqs()
  }
}

const handleAddFaqFromQuestion = async (question: UnresolvedQuestion) => {
  try {
    // 未解決質問からFAQ提案を生成（API呼び出し）
    selectedSuggestion.value = await faqSuggestionApi.generateSuggestion(question.message_id)
    
    // FAQ提案カードまで自動スクロール
    await scrollToSection('faq-suggestion')
  } catch (err: any) {
    console.error('Failed to generate FAQ suggestion:', err)
    // エラーメッセージをユーザーフレンドリーに変換
    let errorMessage = 'FAQ提案の生成に失敗しました'
    const detail = err.response?.data?.detail || err.message || ''
    
    if (detail.includes('Message not found')) {
      errorMessage = 'メッセージが見つかりませんでした。既に削除されている可能性があります。'
    } else if (detail.includes('does not belong to facility')) {
      errorMessage = 'この質問はFAQ提案を生成できません。権限がない可能性があります。'
    } else if (detail) {
      errorMessage = `FAQ提案の生成に失敗しました: ${detail}`
    }
    
    alert(errorMessage)
  }
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
    
    // キャッシュの更新を待つため、少し待ってから再取得
    await new Promise(resolve => setTimeout(resolve, 100))
    // FAQ一覧を再取得
    await fetchFaqs()
    handleCloseForm()
  } catch (err: any) {
    console.error('Failed to save FAQ:', err)
    // エラーメッセージをユーザーフレンドリーに変換
    let errorMessage = 'FAQの保存に失敗しました'
    const detail = err.response?.data?.detail || err.message || ''
    
    if (detail.includes('FAQ not found')) {
      errorMessage = '保存しようとしたFAQが見つかりませんでした。既に削除されている可能性があります。ページをリロードして最新の状態を確認してください。'
    } else if (detail.includes('does not belong to facility')) {
      errorMessage = 'このFAQは保存できません。権限がない可能性があります。'
    } else if (detail.includes('Validation error') || detail.includes('validation')) {
      errorMessage = `入力内容に問題があります: ${detail}`
    } else if (detail) {
      errorMessage = `保存に失敗しました: ${detail}`
    }
    
    alert(errorMessage)
    // エラーが発生しても、FAQ一覧を再取得（キャッシュの問題を回避）
    await fetchFaqs()
  }
}

const handleCloseForm = () => {
  showAddForm.value = false
  editingFaq.value = null
}

const handleApproveSuggestion = async (_suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリアしてFAQ一覧と未解決質問リストを再取得
  selectedSuggestion.value = null
  await fetchFaqs()
  await fetchUnresolvedQuestions()
  // 低評価回答リストを再取得（FAQ承認により処理済みとなった低評価回答を除外）
  await fetchLowRatedAnswers()
}

const handleRejectSuggestion = async (_suggestion: FaqSuggestion) => {
  // API連携はFaqSuggestionCard内で実装済み
  // ここでは提案をクリア
  selectedSuggestion.value = null
  // 低評価回答リストを再取得（画面に反映）
  await fetchLowRatedAnswers()
}

const handleFeedbackImprove = async (answer: LowRatedAnswer) => {
  try {
    console.log('Generating FAQ suggestion for message_id:', answer.message_id)
    console.log('Answer data:', answer)
    // FAQ提案を生成（GPT-4o mini）
    const suggestion = await faqSuggestionApi.generateSuggestion(answer.message_id)
    console.log('FAQ suggestion generated:', suggestion)
    console.log('Suggested question:', suggestion.suggested_question)
    console.log('Suggested answer:', suggestion.suggested_answer)
    
    selectedSuggestion.value = suggestion
    
    // FAQ提案カードまで自動スクロール
    await scrollToSection('faq-suggestion')
  } catch (err: any) {
    console.error('Failed to generate FAQ suggestion:', err)
    console.error('Error details:', err.response?.data || err.message)
    // エラーメッセージをユーザーフレンドリーに変換
    let errorMessage = 'FAQ提案の生成に失敗しました'
    const detail = err.response?.data?.detail || err.message || ''
    
    if (detail.includes('USER role messages') || detail.includes('USER role message') || detail.includes('is USER role')) {
      errorMessage = 'データ不整合が発生しています。USERロールのメッセージに対してFAQ提案を生成することはできません。このメッセージは低評価回答リストから除外されます。管理者にお問い合わせください。'
    } else if (detail.includes('Assistant message is the first message')) {
      errorMessage = 'このメッセージは会話の最初のメッセージです。USERメッセージが存在しないため、FAQ提案を生成できません。データ不整合の可能性があります。管理者にお問い合わせください。'
    } else if (detail.includes('User message not found')) {
      errorMessage = '質問文が見つかりませんでした。データ不整合の可能性があります。管理者にお問い合わせください。'
    } else if (detail.includes('Message not found')) {
      errorMessage = 'メッセージが見つかりませんでした。既に削除されている可能性があります。'
    } else if (detail.includes('does not belong to facility')) {
      errorMessage = 'この質問はFAQ提案を生成できません。権限がない可能性があります。'
    } else if (detail) {
      errorMessage = `FAQ提案の生成に失敗しました: ${detail}`
    }
    
    alert(`❌ エラー: ${errorMessage}\n\n詳細はブラウザのコンソールを確認してください。`)
    // エラー後は提案をクリア（現状維持）
    selectedSuggestion.value = null
  }
}

const ignoringMessageId = ref<number | null>(null)
const showIgnoreConfirm = ref(false)
const pendingIgnoreAnswer = ref<LowRatedAnswer | null>(null)

const handleFeedbackIgnore = (answer: LowRatedAnswer) => {
  console.log('Feedback ignore clicked:', answer)
  // 確認モーダルを表示
  pendingIgnoreAnswer.value = answer
  showIgnoreConfirm.value = true
}

const confirmIgnore = async () => {
  if (!pendingIgnoreAnswer.value) {
    return
  }
  
  const answer = pendingIgnoreAnswer.value
  console.log('Confirm ignore for message_id:', answer.message_id)
  
  // ローディング状態を設定
  ignoringMessageId.value = answer.message_id
  console.log('Calling ignoreNegativeFeedback API for message_id:', answer.message_id)
  
  try {
    await feedbackApi.ignoreNegativeFeedback(answer.message_id)
    console.log('Ignore API call successful')
    // 成功メッセージを表示
    alert('✅ 低評価回答を無視しました。画面から非表示になります。')
    // モーダルを閉じる
    showIgnoreConfirm.value = false
    pendingIgnoreAnswer.value = null
    // 低評価回答リストを再取得（画面に反映）
    await fetchLowRatedAnswers()
    console.log('Low-rated answers list refreshed')
  } catch (err: any) {
    console.error('Failed to ignore negative feedback:', err)
    console.error('Error details:', err.response?.data || err.message)
    const errorMessage = err.response?.data?.detail || err.message || '低評価回答の無視に失敗しました'
    // エラーメッセージを確実に表示
    alert(`❌ エラー: ${errorMessage}\n\n詳細はブラウザのコンソールを確認してください。`)
  } finally {
    // ローディング状態を解除
    ignoringMessageId.value = null
    console.log('Ignore action completed')
  }
}

const handleCancelSuggestion = (_suggestion: FaqSuggestion) => {
  // 提案をクリア（承認・却下せずに閉じる）
  selectedSuggestion.value = null
}
</script>

<style scoped>
/* Component styles */
</style>

