<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        お問い合わせ
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        サポートに関するお問い合わせはこちらから
      </p>
    </div>

    <!-- ローディング表示 -->
    <Loading v-if="loading" />

    <!-- エラー表示 -->
    <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="loadInitialData"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- フォーム -->
    <div v-else class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <form
        ref="formRef"
        action="https://formspree.io/f/mvzzapae"
        method="POST"
        @submit="handleSubmit"
        class="space-y-6"
      >
        <!-- カテゴリ選択（必須） -->
        <div>
          <label for="category" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            カテゴリ <span class="text-red-500">*</span>
          </label>
          <select
            id="category"
            v-model="formData.category"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">カテゴリを選択してください</option>
            <option value="setup">初期設定</option>
            <option value="qrcode">QRコード</option>
            <option value="faq_management">FAQ管理</option>
            <option value="ai_logic">AI仕組み</option>
            <option value="logs">ログ分析</option>
            <option value="troubleshooting">トラブルシューティング</option>
            <option value="billing">料金</option>
            <option value="security">セキュリティ</option>
            <option value="other">その他</option>
          </select>
        </div>

        <!-- メールアドレス（必須） -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            メールアドレス <span class="text-red-500">*</span>
          </label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            name="email"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="example@example.com"
          />
        </div>

        <!-- 施設名称（必須） -->
        <div>
          <label for="facility_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            施設名称 <span class="text-red-500">*</span>
          </label>
          <input
            id="facility_name"
            v-model="formData.facility_name"
            type="text"
            name="facility_name"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：京都ゲストハウス"
          />
        </div>

        <!-- 担当者名（必須） -->
        <div>
          <label for="contact_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            担当者名 <span class="text-red-500">*</span>
          </label>
          <input
            id="contact_name"
            v-model="formData.contact_name"
            type="text"
            name="contact_name"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：山田太郎"
          />
        </div>

        <!-- 件名（任意） -->
        <div>
          <label for="subject" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            件名
          </label>
          <input
            id="subject"
            v-model="formData.subject"
            type="text"
            name="subject"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：FAQ登録について"
          />
        </div>

        <!-- メッセージ（必須） -->
        <div>
          <label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            メッセージ <span class="text-red-500">*</span>
          </label>
          <textarea
            id="message"
            v-model="formData.message"
            name="message"
            required
            rows="8"
            maxlength="2000"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white resize-y"
            placeholder="お問い合わせ内容をご記入ください"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            {{ formData.message.length }} / 2000 文字
          </p>
        </div>

        <!-- エラー時の説明 -->
        <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <h3 class="text-sm font-semibold text-blue-900 dark:text-blue-200 mb-2">
            エラーが発生した場合
          </h3>
          <ul class="text-sm text-blue-800 dark:text-blue-300 space-y-1 list-disc list-inside">
            <li>どの操作をした時に発生したかを教えてください</li>
            <li>エラーメッセージの内容も併せてお知らせください</li>
          </ul>
        </div>

        <!-- マニュアル確認チェック（必須） -->
        <div>
          <label class="flex items-start space-x-3 cursor-pointer">
            <input
              v-model="formData.manual_checked"
              type="checkbox"
              required
              class="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600"
            />
            <span class="text-sm text-gray-700 dark:text-gray-300">
              <span class="text-red-500">*</span> マニュアルを確認しました
            </span>
          </label>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
            <router-link
              to="/admin/manual"
              class="text-indigo-600 dark:text-indigo-400 hover:underline"
            >
              ご利用マニュアルはこちら
            </router-link>
          </p>
        </div>

        <!-- 送信ボタン -->
        <div class="flex items-center justify-center space-x-4">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            <span v-if="!isSubmitting">送信する</span>
            <span v-else class="flex items-center space-x-2">
              <svg class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>送信中...</span>
            </span>
          </button>
        </div>
      </form>

      <!-- 送信成功メッセージ -->
      <div
        v-if="showSuccessMessage"
        class="mt-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4"
      >
        <p class="text-green-800 dark:text-green-200">
          お問い合わせを送信しました。ありがとうございます。
        </p>
      </div>

      <!-- 送信エラーメッセージ -->
      <div
        v-if="submitError"
        class="mt-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
      >
        <p class="text-red-800 dark:text-red-200">
          {{ submitError }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { facilityApi } from '@/api/facility'
import Loading from '@/components/common/Loading.vue'

const { user } = useAuth()

const loading = ref(false)
const error = ref<string | null>(null)
const isSubmitting = ref(false)
const showSuccessMessage = ref(false)
const submitError = ref<string | null>(null)
const formRef = ref<HTMLFormElement | null>(null)

const formData = ref({
  category: '',
  email: '',
  facility_name: '',
  contact_name: '',
  subject: '',
  message: '',
  manual_checked: false
})

// 初期データ読み込み
async function loadInitialData() {
  loading.value = true
  error.value = null

  try {
    // ユーザー情報から自動入力
    if (user.value) {
      formData.value.email = user.value.email || ''
      formData.value.contact_name = user.value.full_name || ''
    }

    // 施設情報を取得して自動入力
    try {
      const facilitySettings = await facilityApi.getFacilitySettings()
      if (facilitySettings.facility) {
        formData.value.facility_name = facilitySettings.facility.name || ''
      }
    } catch (err) {
      // 施設情報の取得に失敗しても続行
      console.warn('Failed to load facility settings:', err)
    }
  } catch (err: any) {
    error.value = err.message || 'データの読み込みに失敗しました'
  } finally {
    loading.value = false
  }
}

// フォーム送信
async function handleSubmit(e: Event) {
  e.preventDefault()
  
  if (!formRef.value) return

  isSubmitting.value = true
  submitError.value = null
  showSuccessMessage.value = false

  try {
    // FormDataを作成
    const formDataObj = new FormData()
    formDataObj.append('category', formData.value.category)
    formDataObj.append('email', formData.value.email)
    formDataObj.append('facility_name', formData.value.facility_name)
    formDataObj.append('contact_name', formData.value.contact_name)
    if (formData.value.subject) {
      formDataObj.append('subject', formData.value.subject)
    }
    formDataObj.append('message', formData.value.message)
    formDataObj.append('manual_checked', formData.value.manual_checked ? '確認済み' : '')

    // Formspreeに送信
    const response = await fetch('https://formspree.io/f/mvzzapae', {
      method: 'POST',
      body: formDataObj,
      headers: {
        'Accept': 'application/json'
      }
    })

    if (response.ok) {
      showSuccessMessage.value = true
      // フォームをリセット
      formData.value = {
        category: '',
        email: user.value?.email || '',
        facility_name: formData.value.facility_name, // 施設名は保持
        contact_name: user.value?.full_name || '',
        subject: '',
        message: '',
        manual_checked: false
      }
      // 成功メッセージを5秒後に非表示
      setTimeout(() => {
        showSuccessMessage.value = false
      }, 5000)
    } else {
      const data = await response.json()
      if (data.errors) {
        submitError.value = data.errors.map((err: any) => err.message).join(', ')
      } else {
        submitError.value = '送信に失敗しました。しばらく時間をおいて再度お試しください。'
      }
    }
  } catch (err: any) {
    submitError.value = 'ネットワークエラーが発生しました。インターネット接続を確認してください。'
    console.error('Form submission error:', err)
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInitialData()
})
</script>

<style scoped>
/* Component styles */
</style>

