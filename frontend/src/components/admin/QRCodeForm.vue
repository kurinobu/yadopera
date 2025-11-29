<template>
  <form @submit.prevent="handleSubmit" class="space-y-6">
    <!-- 設置場所選択 -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        設置場所 <span class="text-red-500">*</span>
      </label>
      <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
        <label
          v-for="location in locations"
          :key="location.value"
          :class="[
            'relative flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer transition-all',
            formData.location === location.value
              ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
              : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500',
            'dark:bg-gray-700'
          ]"
        >
          <input
            v-model="formData.location"
            type="radio"
            :value="location.value"
            class="sr-only"
            required
          />
          <div class="text-center">
            <div class="text-2xl mb-1">{{ location.icon }}</div>
            <div class="text-sm font-medium text-gray-900 dark:text-white">
              {{ location.label }}
            </div>
          </div>
        </label>
      </div>
    </div>

    <!-- カスタム設置場所名入力 -->
    <div v-if="formData.location === 'custom'">
      <Input
        v-model="formData.custom_location_name"
        type="text"
        label="カスタム設置場所名"
        placeholder="例: 受付カウンター"
        :required="true"
        :maxlength="50"
        hint="50文字以内"
        :error="errors.custom_location_name"
      />
    </div>

    <!-- セッション統合トークン埋め込みオプション（v0.3新規） -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-start">
        <input
          v-model="formData.include_session_token"
          type="checkbox"
          id="include-session-token"
          class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <div class="ml-3 flex-1">
          <label
            for="include-session-token"
            class="text-sm font-medium text-gray-900 dark:text-white cursor-pointer"
          >
            セッション統合トークンを埋め込む（v0.3新規）
          </label>
          <p class="mt-1 text-xs text-gray-600 dark:text-gray-400">
            このオプションを有効にすると、QRコードにセッション統合トークンが含まれます。
            ゲストが別デバイスでQRコードを読み取った際、同じトークンで会話履歴を統合できます。
          </p>
        </div>
      </div>
    </div>

    <!-- プレビュー -->
    <div v-if="previewUrl" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">
        QRコードプレビュー
      </h3>
      <div class="flex flex-col items-center">
        <img
          :src="previewUrl"
          alt="QR Code Preview"
          class="w-48 h-48 border border-gray-300 dark:border-gray-600 rounded-lg"
        />
        <p class="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center max-w-xs">
          {{ qrCodeData }}
        </p>
      </div>
    </div>

    <!-- ダウンロードボタン -->
    <div v-if="previewUrl" class="flex items-center justify-center space-x-3">
      <button
        type="button"
        @click="handleDownload('pdf')"
        class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded-lg transition-colors"
      >
        PDF ダウンロード
      </button>
      <button
        type="button"
        @click="handleDownload('png')"
        class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded-lg transition-colors"
      >
        PNG ダウンロード
      </button>
      <button
        type="button"
        @click="handleDownload('svg')"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors"
      >
        SVG ダウンロード
      </button>
    </div>

    <!-- 送信ボタン -->
    <div class="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200 dark:border-gray-700">
      <button
        type="button"
        @click="handleCancel"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
      >
        キャンセル
      </button>
      <button
        type="submit"
        :disabled="!isValid"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        QRコード生成
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Input from '@/components/common/Input.vue'
import type { QRCodeLocation } from '@/types/qrcode'

interface Props {
  facilityId: number
  facilitySlug?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: { location: QRCodeLocation; custom_location_name?: string; include_session_token: boolean }]
  cancel: []
}>()

const locations = [
  { value: 'entrance' as QRCodeLocation, label: '入口', icon: '🚪' },
  { value: 'room' as QRCodeLocation, label: '客室', icon: '🛏️' },
  { value: 'kitchen' as QRCodeLocation, label: 'キッチン', icon: '🍳' },
  { value: 'lounge' as QRCodeLocation, label: 'ラウンジ', icon: '🛋️' },
  { value: 'custom' as QRCodeLocation, label: 'カスタム', icon: '📍' }
]

const formData = ref<{
  location: QRCodeLocation | ''
  custom_location_name: string
  include_session_token: boolean
}>({
  location: '',
  custom_location_name: '',
  include_session_token: false
})

const errors = ref<{
  custom_location_name?: string
}>({})

const previewUrl = ref<string | null>(null)
const qrCodeData = ref<string>('')

const isValid = computed(() => {
  if (formData.value.location === '') {
    return false
  }
  if (formData.value.location === 'custom' && !formData.value.custom_location_name.trim()) {
    return false
  }
  return true
})

// QRコードプレビュー生成（モック）
watch(() => formData.value.location, () => {
  if (formData.value.location && formData.value.location !== 'custom') {
    generatePreview()
  } else if (formData.value.location === 'custom' && formData.value.custom_location_name.trim()) {
    generatePreview()
  } else {
    previewUrl.value = null
    qrCodeData.value = ''
  }
})

watch(() => formData.value.custom_location_name, () => {
  if (formData.value.location === 'custom' && formData.value.custom_location_name.trim()) {
    generatePreview()
  }
})

const generatePreview = () => {
  // モック: QRコードURL生成
  const baseUrl = 'https://yadopera.com'
  const facilitySlug = props.facilitySlug || 'facility-1'
  const location = formData.value.location
  const tokenParam = formData.value.include_session_token ? '&token=AB12' : ''
  
  const url = `${baseUrl}/f/${facilitySlug}?location=${location}${tokenParam}`
  qrCodeData.value = url
  
  // モック: QRコード画像生成（実際の実装ではAPIから取得）
  // ここではQRコード生成ライブラリを使用するか、APIから取得
  // モックとして、QRコードAPIを使用（例: https://api.qrserver.com/v1/create-qr-code/）
  previewUrl.value = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(url)}`
}

const handleSubmit = () => {
  if (formData.value.location === 'custom' && !formData.value.custom_location_name.trim()) {
    errors.value.custom_location_name = 'カスタム設置場所名を入力してください'
    return
  } else {
    delete errors.value.custom_location_name
  }

  if (isValid.value) {
    emit('submit', {
      location: formData.value.location as QRCodeLocation,
      custom_location_name: formData.value.location === 'custom' ? formData.value.custom_location_name.trim() : undefined,
      include_session_token: formData.value.include_session_token
    })
  }
}

const handleCancel = () => {
  emit('cancel')
}

const handleDownload = (format: 'pdf' | 'png' | 'svg') => {
  // TODO: Week 4でAPI連携を実装
  // モック: ダウンロード処理
  console.log(`Download QR code as ${format}`)
  
  if (previewUrl.value) {
    // モック: 実際の実装ではAPIからダウンロードURLを取得
    const link = document.createElement('a')
    link.href = previewUrl.value
    link.download = `qrcode-${formData.value.location}.${format}`
    link.click()
  }
}
</script>

<style scoped>
/* Component styles */
</style>

