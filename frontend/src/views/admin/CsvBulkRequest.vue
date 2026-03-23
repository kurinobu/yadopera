<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        CSV一括登録 代行（有料）の申し込み
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Standard・Premiumプランの施設様向け。FAQ内容をいただき、運営がCSV作成・翻訳・管理画面への登録を行います。
      </p>
    </div>

    <!-- 事前説明 -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 space-y-3">
      <h2 class="text-sm font-semibold text-blue-900 dark:text-blue-200">
        申し込み前にご確認ください
      </h2>
      <ul class="text-sm text-blue-800 dark:text-blue-300 space-y-1 list-disc list-inside">
        <li><strong>FAQの記載例</strong>：QとAを1行ずつ、または「Q:」「A:」のように区切って記載いただくと、CSV変換・翻訳がしやすくなります。</li>
        <li><strong>添付可能な形式</strong>：.xlsx（Excel）、.csv、.txt、.md（Markdown）</li>
        <li><strong>テンプレート</strong>：<a :href="templateCsvUrl" download class="text-indigo-600 dark:text-indigo-400 hover:underline">CSVテンプレート（4言語）をダウンロード</a></li>
      </ul>
    </div>

    <!-- 料金の目安 -->
    <div class="rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50 p-4 space-y-3">
      <h2 class="text-sm font-semibold text-gray-900 dark:text-gray-100">
        料金の目安（税別）
      </h2>
      <div class="overflow-x-auto">
        <table class="min-w-full text-sm text-left text-gray-700 dark:text-gray-300">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-600">
              <th class="py-2 pr-4 font-medium">プラン</th>
              <th class="py-2 pr-4 font-medium">件数</th>
              <th class="py-2 font-medium">料金</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4">Standard（最大100件）</td><td class="py-2 pr-4">〜30件</td><td class="py-2">¥12,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4"></td><td class="py-2 pr-4">〜60件</td><td class="py-2">¥22,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4"></td><td class="py-2 pr-4">〜100件</td><td class="py-2">¥32,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4">Premium（件数無制限）</td><td class="py-2 pr-4">〜50件</td><td class="py-2">¥25,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4"></td><td class="py-2 pr-4">〜100件</td><td class="py-2">¥45,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4"></td><td class="py-2 pr-4">〜200件</td><td class="py-2">¥68,000</td></tr>
            <tr class="border-b border-gray-100 dark:border-gray-700"><td class="py-2 pr-4"></td><td class="py-2 pr-4">200件超</td><td class="py-2">個別見積（¥90,000〜）</td></tr>
          </tbody>
        </table>
      </div>
      <p class="text-xs text-gray-600 dark:text-gray-400">
        <strong>料金に含まれる:</strong> 日本語FAQの自然さ・文法確認、軽微な表現修正、AI翻訳＋品質確認、管理画面への登録作業、表示・動作チェック（初回）。
      </p>
      <p class="text-xs text-gray-600 dark:text-gray-400">
        <strong>料金に含まれない:</strong> FAQの新規企画・構成設計、内容の事実確認、大幅な書き直し・再編集、法的表現監修・翻訳証明。
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
        @submit="handleSubmit"
        class="space-y-6"
      >
        <!-- 施設名 -->
        <div>
          <label for="csv_facility_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            施設名 <span class="text-red-500">*</span>
          </label>
          <input
            id="csv_facility_name"
            v-model="formData.facility_name"
            type="text"
            name="csv_facility_name"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：京都ゲストハウス"
          />
        </div>

        <!-- プラン -->
        <div>
          <label for="csv_plan" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            ご契約プラン <span class="text-red-500">*</span>
          </label>
          <select
            id="csv_plan"
            v-model="formData.plan"
            name="csv_plan"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
          >
            <option value="">選択してください</option>
            <option value="Standard">Standard</option>
            <option value="Premium">Premium</option>
          </select>
        </div>

        <!-- 希望登録件数 -->
        <div>
          <label for="csv_desired_count" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            希望登録件数（目安） <span class="text-red-500">*</span>
          </label>
          <input
            id="csv_desired_count"
            v-model="formData.desired_count"
            type="number"
            name="csv_desired_count"
            required
            min="1"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：30"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">上記の料金目安をご確認のうえ、希望登録件数（目安）をご記入ください。</p>
        </div>

        <!-- 希望言語 -->
        <div>
          <p class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            希望言語（翻訳が必要な言語） <span class="text-red-500">*</span>
          </p>
          <p class="mb-2 text-xs text-gray-500 dark:text-gray-400">
            実際にゲストに提供したい言語をすべて選択してください（日本語も含めてチェック可）。
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            <label
              v-for="lang in languageOptions"
              :key="lang.value"
              class="inline-flex items-center space-x-2 text-sm text-gray-700 dark:text-gray-300"
            >
              <input
                type="checkbox"
                :value="lang.value"
                v-model="formData.languages"
                class="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500 dark:bg-gray-700 dark:border-gray-600"
              />
              <span>{{ lang.label }}</span>
            </label>
          </div>
          <p v-if="languageError" class="mt-1 text-xs text-red-600 dark:text-red-400">
            {{ languageError }}
          </p>
        </div>

        <!-- 連絡メール -->
        <div>
          <label for="csv_email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            連絡メールアドレス <span class="text-red-500">*</span>
          </label>
          <input
            id="csv_email"
            v-model="formData.email"
            type="email"
            name="csv_email"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="example@example.com"
          />
        </div>

        <!-- 担当者名 -->
        <div>
          <label for="csv_contact_name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            担当者名 <span class="text-red-500">*</span>
          </label>
          <input
            id="csv_contact_name"
            v-model="formData.contact_name"
            type="text"
            name="csv_contact_name"
            required
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white"
            placeholder="例：山田太郎"
          />
        </div>

        <!-- FAQ内容の添付 -->
        <div>
          <label for="csv_file" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            FAQ内容のファイル（任意）
          </label>
          <input
            id="csv_file"
            ref="fileInputRef"
            type="file"
            name="csv_faq_file"
            accept=".xlsx,.csv,.txt,.md"
            class="w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-medium file:bg-indigo-50 file:text-indigo-700 dark:file:bg-indigo-900/30 dark:file:text-indigo-300 hover:file:bg-indigo-100 dark:hover:file:bg-indigo-900/50"
          />
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">.xlsx / .csv / .txt / .md いずれか。未作成の場合は申し込み後にメールでお送りいただいても構いません。</p>
        </div>

        <!-- その他要望 -->
        <div>
          <label for="csv_notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            その他要望
          </label>
          <textarea
            id="csv_notes"
            v-model="formData.notes"
            name="csv_notes"
            rows="4"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-md px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-gray-700 dark:text-white resize-y"
            placeholder="ご希望の納期・表現のトーンなど"
          ></textarea>
        </div>

        <!-- 送信ボタン -->
        <div class="flex items-center justify-center">
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
          >
            <span v-if="!isSubmitting">申し込む</span>
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
        <p class="text-green-800 dark:text-green-200 font-medium">
          申し込みを受け付けました。
        </p>
        <p class="mt-1 text-sm text-green-700 dark:text-green-300">
          ご記入のメールアドレス宛に、見積もり・ご案内をお送りします。しばらくお待ちください。
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
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { facilityApi } from '@/api/facility'
import apiClient from '@/api/axios'
import Loading from '@/components/common/Loading.vue'

const { user } = useAuth()

const loading = ref(false)
const error = ref<string | null>(null)
const isSubmitting = ref(false)
const showSuccessMessage = ref(false)
const submitError = ref<string | null>(null)
const formRef = ref<HTMLFormElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)

const formData = ref({
  facility_name: '',
  plan: '',
  desired_count: '' as string | number,
  languages: [] as string[],
  email: '',
  contact_name: '',
  notes: ''
})

const languageOptions = [
  { value: 'ja', label: '日本語' },
  { value: 'en', label: '英語' },
  { value: 'zh-TW', label: '繁体中国語（zh-TW）' },
  { value: 'zh-CN', label: '簡体中国語（zh-CN）' },
  { value: 'fr', label: 'フランス語（fr）' },
  { value: 'ko', label: '韓国語（ko）' },
  { value: 'es', label: 'スペイン語（es）' }
]

const languageError = ref<string | null>(null)

const templateCsvUrl = computed(() => {
  return '/faq-csv-template/FAQ_CSV_template_4lang.csv'
})

async function loadInitialData() {
  loading.value = true
  error.value = null
  try {
    if (user.value) {
      formData.value.email = user.value.email || ''
      formData.value.contact_name = user.value.full_name || ''
    }
    try {
      const facilitySettings = await facilityApi.getFacilitySettings()
      if (facilitySettings.facility) {
        formData.value.facility_name = facilitySettings.facility.name || ''
        if (facilitySettings.facility.plan_type) {
          formData.value.plan = facilitySettings.facility.plan_type
        }
      }
    } catch {
      // ignore
    }
  } catch (err: unknown) {
    error.value = err instanceof Error ? err.message : 'データの読み込みに失敗しました'
  } finally {
    loading.value = false
  }
}

async function handleSubmit(e: Event) {
  e.preventDefault()
  if (!formRef.value) return

  if (formData.value.languages.length === 0) {
    languageError.value = '少なくとも1つ以上の言語を選択してください。'
    return
  } else {
    languageError.value = null
  }

  isSubmitting.value = true
  submitError.value = null
  showSuccessMessage.value = false

  try {
    const formDataObj = new FormData()
    formDataObj.append('csv_facility_name', formData.value.facility_name)
    formDataObj.append('csv_plan', formData.value.plan)
    formDataObj.append('csv_desired_count', String(formData.value.desired_count))
    formDataObj.append('csv_languages', formData.value.languages.join(', '))
    formDataObj.append('csv_email', formData.value.email)
    formDataObj.append('csv_contact_name', formData.value.contact_name)
    formDataObj.append('csv_notes', formData.value.notes)

    const file = fileInputRef.value?.files?.[0]
    if (file) {
      formDataObj.append('csv_faq_file', file)
    }

    await apiClient.post('/admin/csv-bulk-request', formDataObj)

    showSuccessMessage.value = true
    formData.value = {
      facility_name: formData.value.facility_name,
      plan: formData.value.plan,
      desired_count: '',
      languages: [],
      email: user.value?.email || '',
      contact_name: user.value?.full_name || '',
      notes: ''
    }
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 8000)
  } catch (err: unknown) {
    const ax = err as { response?: { status?: number; data?: { detail?: string } } }
    if (ax.response?.status === 503) {
      submitError.value = '申し込み受付は一時的に利用できません。お問い合わせフォームからご連絡ください。'
    } else {
      const detail = ax.response?.data?.detail
      submitError.value = typeof detail === 'string' ? detail : '送信に失敗しました。しばらく時間をおいて再度お試しください。'
    }
  } finally {
    isSubmitting.value = false
  }
}

onMounted(() => {
  loadInitialData()
})
</script>
