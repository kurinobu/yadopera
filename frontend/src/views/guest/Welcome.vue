<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 pb-20">
    <div class="container mx-auto px-4 py-8 max-w-2xl">
      <!-- ローディング表示 -->
      <Loading v-if="isLoading" text="読み込み中..." full-screen />

      <!-- エラー表示 -->
      <div
        v-else-if="error"
        class="mt-8 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      >
        <p class="text-sm text-red-600 dark:text-red-400">
          {{ error }}
        </p>
      </div>

      <!-- メインコンテンツ -->
      <div v-else>
        <!-- 施設情報ヘッダー -->
        <FacilityHeader :facility="facility" />

        <!-- よくある質問TOP3 -->
        <TopQuestions
          :questions="topQuestions"
          @question-click="handleQuestionClick"
        />

        <!-- フリー入力フォーム -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
          <MessageInput
            :disabled="isSubmitting"
            @submit="handleMessageSubmit"
          />
        </div>

        <!-- 緊急連絡先 -->
        <EmergencyContact :facility-phone="facility?.phone" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { facilityApi } from '@/api/facility'
import { useFacilityStore } from '@/stores/facility'
// import { useChatStore } from '@/stores/chat'
import { useSession } from '@/composables/useSession'
import { useOffline } from '@/composables/useOffline'
import FacilityHeader from '@/components/guest/FacilityHeader.vue'
import TopQuestions from '@/components/guest/TopQuestions.vue'
import MessageInput from '@/components/guest/MessageInput.vue'
import EmergencyContact from '@/components/guest/EmergencyContact.vue'
import Loading from '@/components/common/Loading.vue'
import type { TopQuestion } from '@/types/facility'

const route = useRoute()
const router = useRouter()
const facilityStore = useFacilityStore()
// const chatStore = useChatStore()
const { getOrCreateSessionId } = useSession()
const { isOffline } = useOffline()

const facilityId = computed(() => route.params.facilityId as string)
const language = computed(() => (route.query.lang as string) || 'en')
const location = computed(() => (route.query.location as string) || undefined)

const facility = computed(() => facilityStore.currentFacility)
const topQuestions = computed(() => facilityStore.topQuestions)
const isLoading = ref(false)
const isSubmitting = ref(false)
const error = ref<string | null>(null)

// 施設情報を取得
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null

    // TODO: facilityIdからslugを取得する処理（Week 4で実装）
    // 現在はfacilityIdをslugとして使用
    const slug = facilityId.value
    
    const response = await facilityApi.getFacility(slug, location.value)
    
    facilityStore.setFacility(response.facility)
    facilityStore.setTopQuestions(response.top_questions)
  } catch (err: any) {
    // デバッグログ: エラーオブジェクトの構造を確認
    console.error('Facility fetch error:', err)
    console.error('Error code:', err?.code)
    console.error('Error type:', typeof err?.code)
    console.error('Error object keys:', Object.keys(err || {}))
    
    // オフライン時のエラーメッセージ
    // NETWORK_ERRORの場合は、navigator.onLineの値に関わらずオフライン時のメッセージを表示
    const errorCode = err?.code || err?.error?.code
    if (errorCode === 'NETWORK_ERROR' || String(errorCode) === 'NETWORK_ERROR') {
      error.value = '現在オフラインです。インターネット接続を確認してください。'
    } else if (errorCode === 'TIMEOUT_ERROR' || String(errorCode) === 'TIMEOUT_ERROR') {
      error.value = 'リクエストがタイムアウトしました。接続を確認して再度お試しください。'
    } else if (errorCode === 'SERVER_ERROR' || String(errorCode) === 'SERVER_ERROR') {
      error.value = 'サーバーエラーが発生しました。しばらくしてから再度お試しください。'
    } else {
      error.value = '施設情報の取得に失敗しました'
    }
  } finally {
    isLoading.value = false
  }
})

// よくある質問をクリックした場合
const handleQuestionClick = (question: TopQuestion) => {
  // チャット画面に遷移して質問を送信
  router.push({
    name: 'Chat',
    params: { facilityId: facilityId.value },
    query: {
      lang: language.value,
      location: location.value,
      question: question.question
    }
  })
}

// メッセージ送信
const handleMessageSubmit = async (message: string) => {
  if (!facility.value) {
    error.value = '施設情報が取得できませんでした'
    return
  }

  // オフライン時のメッセージ送信をブロック
  if (isOffline.value) {
    error.value = '現在オフラインです。メッセージを送信できません。インターネット接続を確認してください。'
    return
  }

  try {
    isSubmitting.value = true
    error.value = null

    // セッションIDを取得または生成
    getOrCreateSessionId()

    // チャット画面に遷移してメッセージを送信
    router.push({
      name: 'Chat',
      params: { facilityId: facilityId.value },
      query: {
        lang: language.value,
        location: location.value,
        message: message
      }
    })
  } catch (err: any) {
    // デバッグログ: エラーオブジェクトの構造を確認
    console.error('Message submit error:', err)
    console.error('Error code:', err?.code)
    console.error('Error type:', typeof err?.code)
    console.error('Error object keys:', Object.keys(err || {}))
    
    // オフライン時のエラーメッセージ
    // NETWORK_ERRORの場合は、navigator.onLineの値に関わらずオフライン時のメッセージを表示
    const errorCode = err?.code || err?.error?.code
    if (errorCode === 'NETWORK_ERROR' || String(errorCode) === 'NETWORK_ERROR') {
      error.value = '現在オフラインです。インターネット接続を確認してください。'
    } else if (errorCode === 'TIMEOUT_ERROR' || String(errorCode) === 'TIMEOUT_ERROR') {
      error.value = 'リクエストがタイムアウトしました。接続を確認して再度お試しください。'
    } else if (errorCode === 'SERVER_ERROR' || String(errorCode) === 'SERVER_ERROR') {
      error.value = 'サーバーエラーが発生しました。しばらくしてから再度お試しください。'
    } else {
      error.value = 'メッセージの送信に失敗しました'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
/* Component styles */
</style>


