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
            <li><strong>使い方</strong>: 設置場所を選択すると、QRコードのプレビューが自動表示されます</li>
            <li>プレビュー下のボタンから、PDF/PNG/SVG形式でダウンロードできます</li>
            <li>「生成済みQRコード一覧に追加」ボタンで、生成済みQRコード一覧に保存できます</li>
            <li>推奨サイズ: 10cm × 10cm以上（A4印刷用サイズ）</li>
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
          生成済みQRコード一覧
        </h2>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
          このセッションで生成したQRコード。各形式でダウンロードできます。
        </p>
      </div>
      <div class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="qrCode in generatedQRCodes"
            :key="qrCode.id"
            class="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-700"
          >
            <div class="mb-3">
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ getLocationLabel(qrCode.location, qrCode.custom_location_name) }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                {{ formatDateTime(qrCode.created_at) }}
              </p>
            </div>
            <div class="flex items-center justify-center mb-3">
              <img
                :src="qrCode.qr_code_url"
                alt="QR Code"
                class="w-32 h-32 border border-gray-300 dark:border-gray-600 rounded-lg"
              />
            </div>
            <div class="space-y-2">
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
              <button
                @click="handleRemoveFromList(qrCode.id)"
                class="w-full px-3 py-1.5 text-xs font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded transition-colors"
              >
                一覧から削除
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
import type { QRCodeLocation, QRCodeResponse } from '@/types/qrcode'

// データ状態
const loading = ref(false)
const error = ref<string | null>(null)
const facilityId = ref<number | null>(null)
const facilitySlug = ref<string>('')

// interface GeneratedQRCode {
//   id: number
//   location: QRCodeLocation
//   custom_location_name?: string
//   qr_code_url: string
//   qr_code_data: string
//   created_at: string
// }

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

// 生成済みQRコード一覧を取得
const fetchGeneratedQRCodes = async () => {
  try {
    const response = await qrcodeApi.listQRCodes()
    generatedQRCodes.value = response.qr_codes
  } catch (err: any) {
    console.error('Failed to fetch QR codes:', err)
    // エラーは表示しない（初回アクセス時は空の一覧で問題ない）
  }
}

// コンポーネントマウント時に施設情報取得と生成済みQRコード一覧取得
onMounted(async () => {
  await fetchFacilityInfo()
  await fetchGeneratedQRCodes()
})

const getLocationLabel = (location: QRCodeLocation, customLocationName?: string): string => {
  if (location === 'custom' && customLocationName) {
    return customLocationName
  }
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
  format?: 'pdf' | 'png' | 'svg'
}) => {
  if (loading.value || !facilityId.value) return
  
  try {
    loading.value = true
    error.value = null
    
    // データベースに保存するAPIを呼び出し
    await qrcodeApi.generateQRCode({
      location: data.location,
      custom_location_name: data.custom_location_name,
      include_session_token: false,
      format: data.format || 'png'
    })
    
    // データベースから最新の一覧を取得（重複を防ぐため）
    await fetchGeneratedQRCodes()
    // 成功メッセージは表示しない（生成済みQRコード一覧に追加されることが明確）
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

const handleRemoveFromList = async (id: number) => {
  try {
    await qrcodeApi.deleteQRCode(id)
    // 一覧から削除
    const index = generatedQRCodes.value.findIndex(qr => qr.id === id)
    if (index !== -1) {
      generatedQRCodes.value.splice(index, 1)
    }
  } catch (err: any) {
    console.error('Failed to delete QR code:', err)
    alert(err.response?.data?.detail || 'QRコードの削除に失敗しました')
  }
}

const handleDownloadExisting = async (qrCode: QRCodeResponse, format: 'pdf' | 'png' | 'svg') => {
  try {
    let qrCodeUrl: string
    let filename: string

    // 指定された形式でQRコードを再生成（または既存のURLを使用）
    if (qrCode.format === format) {
      // 同じ形式の場合は既存のURLを使用
      qrCodeUrl = qrCode.qr_code_url
      filename = `qrcode-${qrCode.location}-${qrCode.id}.${format}`
    } else {
      // 異なる形式の場合は再生成
      const newQRCode = await qrcodeApi.generateQRCode({
        location: qrCode.location,
        custom_location_name: qrCode.custom_location_name,
        format: format as "svg" | "pdf" | "png",
        include_session_token: false
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

