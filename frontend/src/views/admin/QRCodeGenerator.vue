<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        QRコード発行
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        施設専用QRコードを生成・ダウンロード
      </p>
    </div>

    <!-- 説明 -->
    <div class="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
      <div class="flex items-start">
        <svg
          class="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
            QRコードについて
          </h3>
          <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1 list-disc list-inside">
            <li>設置場所別にQRコードを生成できます</li>
            <li>セッション統合トークンを埋め込むことで、デバイス間で会話履歴を統合できます（v0.3新規）</li>
            <li>PDF/PNG/SVG形式でダウンロード可能（A4印刷用サイズ）</li>
            <li>推奨サイズ: 10cm × 10cm以上</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- エラー表示 -->
    <div v-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
    </div>

    <!-- QRコード発行フォーム -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 p-6">
      <Loading v-if="loading" />
      <QRCodeForm
        v-else
        :facility-id="facilityId || 0"
        :facility-slug="facilitySlug"
        @submit="handleGenerate"
        @cancel="handleCancel"
      />
    </div>

    <!-- 生成済みQRコード一覧 -->
    <div v-if="generatedQRCodes.length > 0" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
      <div class="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
          生成済みQRコード
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          過去に生成したQRコード
        </p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="qrCode in generatedQRCodes"
            :key="qrCode.id"
            class="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div class="flex items-center justify-between mb-3">
              <div>
                <p class="text-sm font-medium text-gray-900 dark:text-white">
                  {{ getLocationLabel(qrCode.location) }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {{ formatDateTime(qrCode.created_at) }}
                </p>
              </div>
              <span
                v-if="qrCode.include_session_token"
                class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200 rounded"
              >
                トークン有り
              </span>
            </div>
            <div class="flex items-center justify-center mb-3">
              <img
                :src="qrCode.qr_code_url"
                alt="QR Code"
                class="w-32 h-32 border border-gray-300 dark:border-gray-600 rounded-lg"
              />
            </div>
            <div class="flex items-center justify-center space-x-2">
              <button
                @click="handleDownloadExisting(qrCode, 'pdf')"
                class="px-3 py-1.5 text-xs font-medium text-white bg-red-600 hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600 rounded transition-colors"
              >
                PDF
              </button>
              <button
                @click="handleDownloadExisting(qrCode, 'png')"
                class="px-3 py-1.5 text-xs font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded transition-colors"
              >
                PNG
              </button>
              <button
                @click="handleDownloadExisting(qrCode, 'svg')"
                class="px-3 py-1.5 text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded transition-colors"
              >
                SVG
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import QRCodeForm from '@/components/admin/QRCodeForm.vue'
import Loading from '@/components/common/Loading.vue'
import { formatDateTime } from '@/utils/formatters'
import { qrcodeApi } from '@/api/qrcode'
import { facilityApi } from '@/api/facility'
import type { QRCodeLocation, QRCodeResponse } from '@/types/qrcode'

// データ状態
const loading = ref(false)
const error = ref<string | null>(null)
const facilityId = ref<number | null>(null)
const facilitySlug = ref<string>('')

interface GeneratedQRCode {
  id: number
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean
  qr_code_url: string
  qr_code_data: string
  created_at: string
}

const generatedQRCodes = ref<QRCodeResponse[]>([])

// 施設情報取得
const fetchFacilityInfo = async () => {
  try {
    // TODO: 施設情報取得APIを実装（現時点ではモック）
    // const facility = await facilityApi.getFacility()
    // facilityId.value = facility.id
    // facilitySlug.value = facility.slug
    facilityId.value = 1
    facilitySlug.value = 'tokyo-guesthouse'
  } catch (err: any) {
    console.error('Failed to fetch facility info:', err)
    error.value = '施設情報の取得に失敗しました'
  }
}

// コンポーネントマウント時に施設情報取得
onMounted(() => {
  fetchFacilityInfo()
})

const getLocationLabel = (location: QRCodeLocation): string => {
  const labels: Record<QRCodeLocation, string> = {
    entrance: '入口',
    room: '客室',
    kitchen: 'キッチン',
    lounge: 'ラウンジ',
    custom: 'カスタム'
  }
  return labels[location]
}

const handleGenerate = async (data: {
  location: QRCodeLocation
  custom_location_name?: string
  include_session_token: boolean
  format: 'pdf' | 'png' | 'svg'
  primary_session_id?: string
}) => {
  if (loading.value || !facilityId.value) return
  
  try {
    loading.value = true
    error.value = null
    
    const qrCode = await qrcodeApi.generateQRCode({
      location: data.location,
      custom_location_name: data.custom_location_name,
      include_session_token: data.include_session_token,
      format: data.format,
      primary_session_id: data.primary_session_id
    })
    
    generatedQRCodes.value.unshift(qrCode)
    alert('QRコードを生成しました。')
  } catch (err: any) {
    console.error('Generate QR code error:', err)
    error.value = err.response?.data?.detail || 'QRコードの生成に失敗しました'
    alert(error.value)
  } finally {
    loading.value = false
  }
}

const handleCancel = () => {
  // フォームをリセット（QRCodeFormコンポーネント内で処理）
}

const handleDownloadExisting = async (qrCode: QRCodeResponse, format: 'pdf' | 'png' | 'svg') => {
  try {
    // 指定された形式でQRコードを再生成（または既存のURLを使用）
    if (qrCode.format === format) {
      // 同じ形式の場合は既存のURLを使用
      const link = document.createElement('a')
      link.href = qrCode.qr_code_url
      link.download = `qrcode-${qrCode.location}-${qrCode.id}.${format}`
      link.click()
    } else {
      // 異なる形式の場合は再生成
      const newQRCode = await qrcodeApi.generateQRCode({
        location: qrCode.location,
        custom_location_name: qrCode.custom_location_name,
        include_session_token: qrCode.include_session_token,
        format: format
      })
      
      const link = document.createElement('a')
      link.href = newQRCode.qr_code_url
      link.download = `qrcode-${newQRCode.location}-${newQRCode.id}.${format}`
      link.click()
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

