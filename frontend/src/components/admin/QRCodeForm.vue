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

    <!-- プレビュー -->
    <div v-if="canGeneratePreview" class="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
      <div class="mb-4">
        <h3 class="text-sm font-medium text-gray-700 dark:text-gray-300">
          QRコードプレビュー
        </h3>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
          設置場所を選択すると、QRコードが自動生成されます。下のボタンからダウンロードできます。
        </p>
      </div>
      
      <!-- ローディング状態 -->
      <div v-if="previewLoading" class="flex flex-col items-center justify-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mb-4"></div>
        <p class="text-sm text-gray-500 dark:text-gray-400">QRコードを生成中...</p>
      </div>

      <!-- エラー状態 -->
      <div v-else-if="previewError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
        <p class="text-sm text-red-800 dark:text-red-200">{{ previewError }}</p>
      </div>

      <!-- プレビュー表示 -->
      <div v-else-if="previewUrl" class="flex flex-col items-center">
        <img
          :src="previewUrl"
          alt="QR Code Preview"
          class="w-48 h-48 border border-gray-300 dark:border-gray-600 rounded-lg"
        />
        <p class="mt-4 text-xs text-gray-500 dark:text-gray-400 text-center max-w-xs break-all">
          {{ qrCodeData }}
        </p>
      </div>

      <!-- ダウンロードボタン -->
      <div v-if="previewUrl && !previewLoading" class="mt-6 flex items-center justify-center space-x-3">
        <button
          type="button"
          @click="handleDownload('pdf')"
          class="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          PDF ダウンロード
        </button>
        <button
          type="button"
          @click="handleDownload('png')"
          class="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          PNG ダウンロード
        </button>
        <button
          type="button"
          @click="handleDownload('svg')"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          SVG ダウンロード
        </button>
      </div>
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
        :disabled="!isValid || previewLoading"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        生成済みQRコード一覧に追加
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Input from '@/components/common/Input.vue'
import { qrcodeApi } from '@/api/qrcode'
import type { QRCodeLocation, QRCodeResponse } from '@/types/qrcode'

interface Props {
  facilityId: number
  facilitySlug?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: { location: QRCodeLocation; custom_location_name?: string; format?: 'pdf' | 'png' | 'svg' }]
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
}>({
  location: '',
  custom_location_name: ''
})

const errors = ref<{
  custom_location_name?: string
}>({})

const previewLoading = ref(false)
const previewError = ref<string | null>(null)
const previewQRCode = ref<QRCodeResponse | null>(null)
const previewUrl = ref<string | null>(null)
const qrCodeData = ref<string>('')

// デバウンス用のタイマー
let previewDebounceTimer: NodeJS.Timeout | null = null

const isValid = computed(() => {
  if (formData.value.location === '') {
    return false
  }
  if (formData.value.location === 'custom' && !formData.value.custom_location_name.trim()) {
    return false
  }
  return true
})

const canGeneratePreview = computed(() => {
  if (!formData.value.location) return false
  if (formData.value.location === 'custom' && !formData.value.custom_location_name.trim()) {
    return false
  }
  return true
})

// プレビュー生成（実際のAPIを使用）
const generatePreview = async () => {
  if (!canGeneratePreview.value || !props.facilityId) {
    previewUrl.value = null
    qrCodeData.value = ''
    previewQRCode.value = null
    return
  }

  // デバウンス処理（500ms待機）
  if (previewDebounceTimer) {
    clearTimeout(previewDebounceTimer)
  }

  previewDebounceTimer = setTimeout(async () => {
    try {
      previewLoading.value = true
      previewError.value = null

      // プレビュー用APIを呼び出し（データベースに保存しない）
      const qrCode = await qrcodeApi.generateQRCodePreview({
        location: formData.value.location as QRCodeLocation,
        custom_location_name: formData.value.location === 'custom' ? formData.value.custom_location_name.trim() : undefined,
        format: 'png' // プレビューはPNG形式
      })

      previewQRCode.value = qrCode
      previewUrl.value = qrCode.qr_code_url
      qrCodeData.value = qrCode.qr_code_data
    } catch (err: any) {
      console.error('Preview generation error:', err)
      previewError.value = err.response?.data?.detail || 'プレビューの生成に失敗しました'
      previewUrl.value = null
      qrCodeData.value = ''
      previewQRCode.value = null
    } finally {
      previewLoading.value = false
    }
  }, 500)
}

// 設置場所変更時にプレビューを生成
watch(() => formData.value.location, () => {
  if (formData.value.location && formData.value.location !== 'custom') {
    generatePreview()
  } else if (formData.value.location === 'custom' && formData.value.custom_location_name.trim()) {
    generatePreview()
  } else {
    previewUrl.value = null
    qrCodeData.value = ''
    previewQRCode.value = null
  }
})

// カスタム設置場所名変更時にプレビューを生成
watch(() => formData.value.custom_location_name, () => {
  if (formData.value.location === 'custom' && formData.value.custom_location_name.trim()) {
    generatePreview()
  }
})


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
      format: 'png' // デフォルト形式
    })
  }
}

const handleCancel = () => {
  emit('cancel')
}

/**
 * Data URLをBlobに変換してダウンロードする
 */
const downloadDataUrl = (dataUrl: string, filename: string) => {
  // Data URL形式を解析
  const matches = dataUrl.match(/^data:([^;]+);base64,(.+)$/)
  if (!matches) {
    // Data URL形式でない場合は直接ダウンロードを試みる
    const link = document.createElement('a')
    link.href = dataUrl
    link.download = filename
    link.target = '_blank'
    link.click()
    return
  }

  const mimeType = matches[1]
  const base64Data = matches[2]

  // Base64データをバイナリに変換
  const byteCharacters = atob(base64Data)
  const byteNumbers = new Array(byteCharacters.length)
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i)
  }
  const byteArray = new Uint8Array(byteNumbers)

  // Blobを作成
  const blob = new Blob([byteArray], { type: mimeType })
  const blobUrl = URL.createObjectURL(blob)

  // ダウンロードリンクを作成
  const link = document.createElement('a')
  link.href = blobUrl
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  // Blob URLを解放（メモリリーク防止）
  setTimeout(() => {
    URL.revokeObjectURL(blobUrl)
  }, 100)
}

const handleDownload = async (format: 'pdf' | 'png' | 'svg') => {
  if (!previewQRCode.value) {
    alert('QRコードが生成されていません。')
    return
  }

  try {
    let qrCodeUrl: string
    let filename: string

    // 指定された形式でQRコードを再生成（または既存のURLを使用）
    if (previewQRCode.value.format === format) {
      // 同じ形式の場合は既存のURLを使用
      qrCodeUrl = previewQRCode.value.qr_code_url
      filename = `qrcode-${previewQRCode.value.location}-${previewQRCode.value.id}.${format}`
    } else {
      // 異なる形式の場合は再生成（データベースに保存しない）
      const newQRCode = await qrcodeApi.generateQRCodePreview({
        location: previewQRCode.value.location,
        custom_location_name: previewQRCode.value.custom_location_name,
        format: format
      })
      qrCodeUrl = newQRCode.qr_code_url
      filename = `qrcode-${newQRCode.location}-${newQRCode.id}.${format}`
    }

    // Data URL形式の場合はBlobに変換してダウンロード
    if (qrCodeUrl.startsWith('data:')) {
      downloadDataUrl(qrCodeUrl, filename)
    } else {
      // 外部URLの場合は直接ダウンロードを試みる
      const link = document.createElement('a')
      link.href = qrCodeUrl
      link.download = filename
      link.target = '_blank'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  } catch (err: any) {
    console.error('Download QR code error:', err)
    alert(err.response?.data?.detail || 'QRコードのダウンロードに失敗しました')
  }
}
</script>

<style scoped>
/* Component styles */
</style>

